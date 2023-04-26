"""CLI utilities connected to auth"""
import gc
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


async def _initialize(force: bool = False):
    """Initializes the auth service"""
    settings.initialize()

    global hymns_service_conf
    if force or hymns_service_conf is None:
        hymns_service_conf = settings.get_hymns_service_config()
        await config.save_service_config(
            settings.get_config_db_uri(), hymns_service_conf
        )

    global auth_service
    if force or auth_service is None:
        auth_service = await auth.initialize(
            config_db_uri=settings.get_config_db_uri(),
            service_db_uri=settings.get_auth_db_uri(),
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


async def create_account(username: str, email: str, password: str):
    """Creates a new admin account"""
    try:
        await _initialize()

        user = await auth_service.users_store.get(username)
        if user is not None:
            raise ValueError("user already exists")

        res = await auth.create_user(
            auth_service, UserDTO(username=username, email=email, password=password)
        )
        result = _handle_result(res)
    finally:
        await _shutdown()

    return result


async def delete_account(username: str, password: str):
    """Deletes the account whose username and password are given"""
    try:
        await _initialize()

        user = await auth.get_user_with_credentials(
            auth_service, username=username, password=password
        )
        if user is None:
            raise auth.errors.AuthenticationError("invalid credentials")

        res = await auth.remove_user(auth_service, username=username)
        result = _handle_result(res)
    finally:
        await _shutdown()

    return result


async def change_password(username: str, old_password: str, new_password: str):
    """Changes the password of the account"""
    try:
        await _initialize()

        res = await auth.change_password(
            auth_service,
            data=ChangePasswordRequest(
                original_password=old_password,
                new_password=new_password,
                username=username,
            ),
        )
        result = _handle_result(res)
    finally:
        await _shutdown()

    return result


async def login(username: str, password: str):
    """Attempts to log the user in"""
    try:
        await _initialize()

        res = await auth.login(
            auth_service,
            username=username,
            password=password,
            otp_verification_url=otp_verification_url,
        )
        result = _handle_result(res)
    finally:
        await _shutdown()

    return result


async def _shutdown():
    """Gracefully shuts down after the app is finished"""
    await Store.destroy_stores()
    global auth_service
    auth_service = None

    global hymns_service_conf
    hymns_service_conf = None

    global otp_verification_url
    otp_verification_url = None

    gc.collect()


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
