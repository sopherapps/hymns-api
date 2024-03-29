import os
from pathlib import Path

import aiosmtplib.smtp
import dotenv
import fastapi_mail

from errors import ConfigurationError
from services.config import ServiceConfig

_root_path = os.path.dirname(os.path.abspath(__file__))
_default_db_path = os.path.join(_root_path, "db")
_default_env_file = os.path.join(_root_path, ".env")


def initialize():
    """Initializes the settings basing on app settings"""
    if os.getenv("APP_SETTINGS", "production") != "testing":
        dotenv.load_dotenv(_default_env_file)


def get_db_uri() -> str:
    """Gets the db path for the app"""
    return os.getenv("DB_PATH", _default_db_path)


def get_auth_db_uri() -> str:
    """Gets the db uri for the auth service"""
    return os.getenv("AUTH_DB_URI", get_db_uri())


def get_config_db_uri() -> str:
    """Gets the db uri for the config"""
    return os.getenv("CONFIG_DB_PATH", get_db_uri())


def get_hymns_db_uri() -> str:
    """Gets the db uri for the hymns service"""
    return os.getenv("HYMNS_DB_PATH", get_db_uri())


def get_hymns_service_config() -> ServiceConfig:
    """Gets the service config for the hymns service"""
    return ServiceConfig(
        max_keys=int(os.getenv("MAX_HYMNS", "2_000_000")),
        redundant_blocks=int(os.getenv("DB_REDUNDANCY_BLOCKS", "2")),
        pool_capacity=int(os.getenv("DB_BUFFER_POOL_CAPACITY", "5")),
        compaction_interval=int(os.getenv("DB_COMPACTION_INTERVAL", "3600")),
        languages=[
            lang.strip()
            for lang in os.getenv("LANGUAGES", "english,runyoro").split(",")
        ],
    )


# FastAPI
def get_api_key_length() -> int:
    """Gets the length of all API KEY's that will be generated"""
    return int(os.getenv("API_KEY_LENGTH", "32"))


def get_rate_limit() -> str:
    """Gets the rate limit for all routes"""
    return os.getenv("RATE_LIMIT", "5/minute")


def get_otp_verification_url() -> str:
    """The URL where the form for verification of OTP for admin users is."""
    try:
        return os.getenv("OTP_VERIFICATION_URL")
    except KeyError:
        raise ConfigurationError("environment variable 'OTP_VERIFICATION_URL' not set")


def get_api_secret() -> str:
    """Gets the API secret for use in hashing password

    Raises:
        KeyError: API_SECRET
    """
    try:
        return os.environ["API_SECRET"]
    except KeyError:
        raise ConfigurationError("environment variable 'API_SECRET' not set")


def get_jwt_ttl_in_sec() -> float:
    """Gets the JWT TTL in seconds

    Returns:
        the time to live in seconds
    """
    return float(os.getenv("JWT_TTL_SECONDS", "900").strip())


def get_is_rate_limit_enabled() -> bool:
    """Gets the configuration flag of whether the rate limit is enabled or not"""
    env_str = os.getenv("ENABLE_RATE_LIMIT", "true").strip()
    if env_str.lower() == "true":
        return True
    return False


def get_max_login_attempts() -> int:
    """Gets the configuration for the maximum login attempts (OTP verifications) for a given User.

    Returns:
        the maximum login attempts
    """
    return int(os.getenv("MAX_LOGIN_ATTEMPTS", "5").strip())


def get_auth_email_sender() -> str:
    """Gets the name to be added in the auth emails as the sender in the "best regards" section.

    Returns:
        the name to be added in the auth emails as the sender in the "best regards" section
    """
    return os.getenv("AUTH_MAIL_SENDER", "Hymns API team")


def get_email_config() -> fastapi_mail.ConnectionConfig:
    """Gets the email connection configuration for the app.

    Returns:
        the email connection configuration to be used by the application
    """
    return fastapi_mail.ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_PORT=int(os.getenv("MAIL_PORT")),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_STARTTLS=_str_to_bool(os.getenv("MAIL_STARTTLS", "true")),
        MAIL_SSL_TLS=_str_to_bool(os.getenv("MAIL_SSL_TLS", "false")),
        MAIL_DEBUG=int(os.getenv("MAIL_DEBUG", "0")),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", None),
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
        SUPPRESS_SEND=int(os.getenv("MAIL_SUPPRESS_SEND", "0")),
        USE_CREDENTIALS=_str_to_bool(os.getenv("MAIL_USE_CREDENTIALS", "true")),
        VALIDATE_CERTS=_str_to_bool(os.getenv("MAIL_VALIDATE_CERTS", "true")),
        TIMEOUT=int(os.getenv("MAIL_TIMEOUT", f"{aiosmtplib.smtp.DEFAULT_TIMEOUT}")),
    )


def _str_to_bool(value: str) -> bool:
    """converts string to boolean"""
    return value.strip().lower() == "true"
