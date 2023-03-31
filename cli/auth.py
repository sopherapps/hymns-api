"""CLI utilities connected to auth"""
from typing import Optional

import funml as ml
import settings
from services import auth, config
from services.auth.models import UserDTO, ChangePasswordRequest
from services.auth.types import AuthService
from services.store import Store

auth_service: Optional[AuthService] = None
hymns_service_conf: Optional[config.ServiceConfig] = None
otp_verification_url: Optional[str] = None
is_initialized: bool = False


async def initialize(force: bool = False):
    """Initializes the auth service"""
    global hymns_service_conf
    if force or hymns_service_conf is None:
        hymns_service_conf = settings.get_hymns_service_config()
        await config.save_service_config(
            settings.get_config_db_uri(), hymns_service_conf
        )

    global auth_service
    if force or auth_service is None:
        auth_service = await auth.initialize(
            uri=settings.get_auth_db_uri(),
            key_size=settings.get_api_key_length(),
            api_secret=settings.get_api_secret(),
            jwt_ttl=settings.get_jwt_ttl_in_sec(),
            max_login_attempts=settings.get_max_login_attempts(),
            mail_config=settings.get_email_config(),
            mail_sender=settings.get_auth_email_sender(),
        )

    global otp_verification_url
    if force or otp_verification_url is None:
        otp_verification_url = settings.get_otp_verification_url()

    global is_initialized
    if force or not is_initialized:
        await Store.setup_stores()


async def create_account(username: str, email: str, password: str):
    """Creates a new admin account"""
    await initialize()

    user = await auth_service.users_store.get(UserDTO, username)
    if user is not None:
        raise ValueError("user already exists")

    res = await auth.create_user(
        auth_service, UserDTO(username=username, email=email, password=password)
    )
    return _handle_result(res)


async def delete_account(username: str, password: str):
    """Deletes the account whose username and password are given"""
    await initialize()

    user = await auth.get_user_with_credentials(
        auth_service, username=username, password=password
    )
    if user is None:
        raise auth.errors.AuthenticationError("invalid credentials")

    res = await auth.remove_user(auth_service, username=username)
    return _handle_result(res)


async def change_password(username: str, old_password: str, new_password: str):
    """Changes the password of the account"""
    await initialize()

    res = await auth.change_password(
        auth_service,
        data=ChangePasswordRequest(
            original_password=old_password,
            new_password=new_password,
            username=username,
        ),
    )
    return _handle_result(res)


async def login(username: str, password: str):
    """Attempts to log the user in"""
    await initialize()

    res = await auth.login(
        auth_service,
        username=username,
        password=password,
        otp_verification_url=otp_verification_url,
    )
    return _handle_result(res)


async def shutdown():
    """Gracefully shuts down after the app is finished"""
    await Store.destroy_stores()


def _handle_result(res: ml.Result):
    """Handles an ml.Result result"""
    return (
        ml.match(res)
        .case(ml.Result.ERR(Exception), do=_raise_exception)
        .case(ml.Result.OK(...), do=lambda v: v)()
    )


def _raise_exception(exp: Exception):
    """Raises an exception given a given exception"""
    raise exp
