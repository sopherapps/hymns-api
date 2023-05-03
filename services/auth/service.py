"""Handles all authentication and authorization"""
from datetime import timedelta
from typing import Union, Dict, Any, Optional

import fastapi_mail
import funml as ml
import pyotp
from cryptography.fernet import Fernet

from services.auth.types import AuthService
from services.config import get_auth_store, get_users_store, get_service_config
from .errors import AuthenticationError, OTPVerificationError
from .models import (
    UserInDb,
    LoginResponse,
    UserDTO,
    ChangePasswordRequest,
    OTPResponse,
    Application,
)
from .utils import (
    generate_random_key,
    is_password_match,
    decode_jwt,
    encrypt_str,
    generate_access_token,
    decrypt_str,
    hash_password,
)
from ..errors import NotFoundError

_ALGORITHM = "HS256"


async def initialize(
    config_db_uri: Union[bytes, str],
    service_db_uri: Union[bytes, str],
    key_size: int,
    api_secret: str,
    jwt_ttl: float,
    max_login_attempts: int,
    mail_config: fastapi_mail.ConnectionConfig,
    mail_sender: str,
) -> "AuthService":
    """Initializes the auth service given the root path to the configuration store.

    Args:
        config_db_uri: the path to the store for the configuration service
        service_db_uri: the path to the stores for the hymns service
        key_size: the size of the API key to be used
        api_secret: the API secret for handling cryptographic things
        jwt_ttl: time-to-live for the JWT in seconds
        max_login_attempts: the maximum OTP verification attempts permissible for any user
        mail_config: the Mail ConnectionConfig for sending emails
        mail_sender: the name to be added to the emails as sender in the 'best regards' section

    Returns:
        the HymnsService whose configuration is at the store_uri
    """
    service_conf = await get_service_config(config_db_uri)
    auth_store = get_auth_store(service_conf=service_conf, uri=service_db_uri)
    users_store = get_users_store(service_conf=service_conf, uri=service_db_uri)
    fernet = Fernet(api_secret)
    return AuthService(
        auth_store=auth_store,
        users_store=users_store,
        key_size=key_size,
        api_secret=api_secret,
        fernet=fernet,
        jwt_ttl=jwt_ttl,
        max_login_attempts=max_login_attempts,
        mail=fastapi_mail.FastMail(mail_config),
        mail_sender=mail_sender,
    )


async def register_app(service: AuthService) -> ml.Result:
    """Registers a new application with the auth service if its name does not exist already

    It saves the application with a hashed key in the auth_store but returns the application
    with its original key.

    Args:
        service: the auth service where the application is registered

    Returns:
        the created application with its raw key

    Raises:
        Exception: failed to create unique application key
    """
    try:
        key = generate_random_key(service.key_size)
        _app = await service.auth_store.get(key)

        if _app is not None:
            raise Exception(f"failed to create unique application key")

        _app = Application(key=key)
        await service.auth_store.set(key, _app)

        return ml.Result.OK(_app)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def is_valid_api_key(service: AuthService, key: str) -> bool:
    """Checks the validity of the given api key.

    Args:
        service: the auth service where the key is to be validated from
        key: the api key to be validated

    Returns:
        true if key is valid else false
    """
    res = await service.auth_store.get(key)
    return res is not None


async def change_password(
    service: AuthService, data: ChangePasswordRequest
) -> ml.Result:
    """Attempts to change the password of the user of the given username.

    Args:
        service: the auth service responsible for changing the user's password
        data: the data containing the old password and the new password, and the username

    Returns:
        the ml.Result.OK(None) if the change is successful or else it returns the ml.Result.ERR
    """
    try:
        user = await _get_user(service, username=data.username)
        if user is None:
            # intentionally given a vague error message to discourage hackers
            raise AuthenticationError("username and password don't match")

        if not is_password_match(data.original_password, user.password):
            raise AuthenticationError("username and password don't match")

        await _update_user(
            service, user=user, password=hash_password(data.new_password)
        )
        return ml.Result.OK(None)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def create_user(service: AuthService, user: UserDTO) -> ml.Result:
    """Attempts to create a user.

    If the username of the user already exists, a Conflict Error will be returned.

    Args:
        service: the auth service where the user is to be created
        user: the user to be created

    Returns:
        an ml.Result.OK with the newly created user or an ml.Result.ERR if an error occurs
    """
    user_in_db = UserInDb(
        username=user.username,
        email=encrypt_str(service.fernet, user.email),
        password=hash_password(user.password),
        otp_counter=encrypt_str(service.fernet, "0"),
        otp_secret=encrypt_str(service.fernet, pyotp.random_base32()),
        login_attempts=0,
    )
    try:
        await service.users_store.set(user.username, user_in_db)
        return ml.Result.OK(user)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def update_user(
    service: AuthService, username: str, data: Dict[str, Any]
) -> ml.Result:
    """Attempts to update a user.

    Ignores changes to the username, and any unknown fields

    Args:
        service: the auth service where the user is to be updated
        username: the username of the user to be updated
        data: the new data to add to the user

    Returns:
        an ml.Result.OK(UserDTO) with the newly updated user or an ml.Result.ERR if an error occurs
    """
    try:
        user = await _get_user(service, username=username)

        if user is None:
            raise NotFoundError(username)

        encrypted_data = _encrypt_user_props(service, data)
        try:
            encrypted_data["password"] = hash_password(encrypted_data["password"])
        except KeyError:
            pass

        new_user = await _update_user(service, user=user, **encrypted_data)
        return ml.Result.OK(UserDTO.from_user_in_db(new_user))
    except Exception as exp:
        return ml.Result.ERR(exp)


async def remove_user(service: AuthService, username: str) -> ml.Result:
    """Attempts to delete the user of the given username

    Args:
        service: the auth service where the user was removed
        username: the username of the user to be deleted

    Returns:
        an ml.Result.OK(UserDTO) with the newly deleted user or an ml.Result.ERR if an error occurs
    """
    try:
        users = await service.users_store.delete(username)

        if len(users) == 0:
            raise NotFoundError(username)

        return ml.Result.OK(UserDTO.from_user_in_db(users[0]))
    except Exception as exp:
        return ml.Result.ERR(exp)


async def get_current_user(service: AuthService, token: str) -> ml.Result:
    """Gets the current user attached to the given token.

    Args:
        service: the auth service where the authenticated user is to be got
        token: the JWT token for the given user

    Returns:
        ml.Result.OK(UserDTO) if the token is o a valid user or else ml.Result.ERR()
    """
    try:
        user = await _get_user_in_jwt(service, token=token, is_verified=True)
        return ml.Result.OK(UserDTO.from_user_in_db(user))
    except Exception as exp:
        return ml.Result.ERR(exp)


async def login(
    service: AuthService, username: str, password: str, otp_verification_url: str
) -> ml.Result:
    """Attempts to login the user with the given username and password

    It creates a JWT token that is not yet approved to be used until the OTP is
    submitted and verified

    Args:
        service: the auth service where the authenticated user is to be got
        username: the username of the authenticated user
        password: the password of the authenticated user
        otp_verification_url: the url for verifying the OTP

    Returns:
        ml.Result.OK(LoginResponse) if the username and password match or else ml.Result.ERR()
    """
    user = await get_user_with_credentials(
        service, username=username, password=password
    )

    if user:
        user.login_attempts = 0
        await service.users_store.set(user.username, user)

        otp = _generate_otp(service, user=user)
        await _send_email(
            service,
            user=user,
            title="Your OTP for Your Login Attempt",
            msg=f"Your OTP for your latest login attempt is {otp}. Submit it at {otp_verification_url}",
        )

        unverified_jwt = _generate_jwt(service, username=user.username, verified=False)
        resp = LoginResponse(
            access_token=unverified_jwt,
            message=f"an OTP was sent to your email. Submit it at {otp_verification_url}",
        )
        return ml.Result.OK(resp)

    return ml.Result.ERR(AuthenticationError("username and password don't match"))


async def get_user_with_credentials(
    service: AuthService, username: str, password: str
) -> Optional[UserInDb]:
    """Gets the user whose credentials are those that are given"""
    user = await _get_user(service, username=username)

    if isinstance(user, UserInDb) and is_password_match(
        raw_password=password, hashed_password=user.password
    ):
        return user


async def verify_otp(
    service: AuthService, otp: str, unverified_token: str
) -> ml.Result:
    """Verifies the OTP given the unverified JWT token

    Returns:
        an ml.Result.OK(Tuple[OTPResponse, UserDTO]) of the verified JWT token if the OTP is right for the given token

    Raises:
        OTPVerificationError: maximum attempts to verify OTP
        OTPVerificationError: invalid OTP
    """
    try:
        user = await _get_user_in_jwt(
            service, token=unverified_token, is_verified=False
        )
        if user.login_attempts >= service.max_login_attempts:
            await _send_email(
                service,
                user=user,
                title="You Have Maxed Out OTP Verification Attempts",
                msg="Someone has tried to verify an OTP multiple times and they have gone beyond the permissible limits. If it is not you, please change your password immediately",
            )
            raise OTPVerificationError("maximum attempts to verify OTP")

        if not _is_otp_valid(service, user=user, otp=otp):
            await _update_user(
                service, user=user, login_attempts=user.login_attempts + 1
            )
            raise OTPVerificationError("invalid OTP")
        else:
            otp_counter = int(decrypt_str(service.fernet, user.otp_counter))
            user.otp_counter = encrypt_str(service.fernet, f"{otp_counter + 1}")
            await _update_user(service, user=user, login_attempts=0)

            verified_jwt = _generate_jwt(service, username=user.username, verified=True)
            return ml.Result.OK(
                (OTPResponse(access_token=verified_jwt), UserDTO.from_user_in_db(user))
            )
    except Exception as exp:
        return ml.Result.ERR(exp)


def _encrypt_user_props(service: AuthService, data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypts any user data that is in data.

    Args:
        service: the auth service that is in charge of encrypting the user data
        data: the raw unencrypted data

    Returns:
        the encrypted data got from data
    """
    encryptable_fields = ("email", "otp_counter", "otp_secret")
    return {
        k: encrypt_str(service.fernet, v) if k in encryptable_fields else v
        for k, v in data.items()
    }


async def _update_user(service: AuthService, user: UserInDb, **kwargs) -> UserInDb:
    """Updates the user, saving the new user in hte database and returning the updated user.

    Args:
        service: the AuthService for handling saving the user
        user: the original user
        kwargs: the new properties to update on the user

    Returns:
        the updated user
    """
    new_data = {**user.dict(), **kwargs, "username": user.username}
    new_user = UserInDb(**new_data)
    await service.users_store.set(user.username, new_user)
    return new_user


def _is_otp_valid(service: AuthService, user: UserInDb, otp: str) -> bool:
    """Checks whether the OTP is valid or not for the given user.

    Args:
        service: the AuthService that is to handle the validation of the given OTP
        user: the User associated with the given OTP
        otp: the one-time password to be validated

    Returns:
        True if the otp is valid for the given user or False if it is not
    """
    otp_secret = decrypt_str(service.fernet, user.otp_secret)
    otp_counter = int(decrypt_str(service.fernet, user.otp_counter))
    return pyotp.HOTP(otp_secret).verify(otp, otp_counter)


def _generate_jwt(service: AuthService, username: str, verified: bool) -> str:
    """Generates the JWT for the given username

    Args:
        username: the username to associate the JWT to a given user
        verified: whether the JWT should be verified or not

    Returns:
        the JWT
    """
    encrypted_username = encrypt_str(service.fernet, word=username)
    ttl = timedelta(seconds=service.jwt_ttl)
    return generate_access_token(
        _id=encrypted_username,
        secret_key=service.api_secret,
        ttl=ttl,
        algorithm=_ALGORITHM,
        verified=verified,
    )


def _generate_otp(service: AuthService, user: UserInDb) -> str:
    """Generates the OTP(one-time password) to be used for the given user

    Args:
        service: the auth service to handle the OTP generation
        user: the user to which the given OTP is attached

    Returns:
        the OTP
    """
    otp_secret = decrypt_str(service.fernet, user.otp_secret)
    otp_counter = int(decrypt_str(service.fernet, user.otp_counter))
    return pyotp.HOTP(otp_secret).at(otp_counter)


async def _get_user_in_jwt(
    service: AuthService, token: str, is_verified: bool = True
) -> UserInDb:
    """Gets the user associated with the given JWT token

    Args:
        service: the auth service to handle the decoding of the JWT
        token: the JWT token
        is_verified: whether the JWT token is verified or not

    Returns:
        the UserInDb

    Raises:
        OTPVerificationError: the one time password sent to you has not been verified yet
        AuthenticationError: invalid token
    """
    payload = decode_jwt(token, secret_key=service.api_secret, algorithm=_ALGORITHM)
    if is_verified and not payload["verified"]:
        raise OTPVerificationError(
            "the one time password sent to you has not been verified yet"
        )

    encrypted_username = payload["sub"]
    username = decrypt_str(service.fernet, word=encrypted_username)

    user = await _get_user(service, username=username)
    if user is None:
        raise AuthenticationError("invalid token")

    return user


async def _send_email(
    service: AuthService,
    user: UserInDb,
    title: str,
    msg: str,
    template: Optional[str] = "emails/default.html",
):
    """Sends an email to the user

    Args:
        service: the auth service to handle the sending of the otp
        user: the user to whom the otp is to be sent
        title: the reference subject of the email
        msg: the main message to send to user
        template: the HTML template to use to send the email
    """
    email = decrypt_str(service.fernet, user.email)
    message = fastapi_mail.MessageSchema(
        recipients=[email],
        subject=title,
        template_body={
            "msg": msg,
            "sender_name": service.mail_sender,
            "name": user.username,
        },
        subtype=fastapi_mail.MessageType.html,
    )
    await service.mail.send_message(message, template_name=template)


async def _get_user(service: AuthService, username: str) -> Optional[UserInDb]:
    """Attempts to get the user whose username is given.

    Args:
        service: the auth service where the user is to be got
        username: the username of the user to be retrieved

    Returns:
        user of the given username or None if there is no user
    """
    user: Optional[UserInDb] = await service.users_store.get(username)
    return user
