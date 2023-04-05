"""All types for the auth service"""
import fastapi_mail
from cryptography.fernet import Fernet

from services.store.base import Store


class AuthService:
    def __init__(
        self,
        auth_store: Store,
        users_store: Store,
        api_secret: str,
        key_size: int,
        fernet: Fernet,
        jwt_ttl: float,
        max_login_attempts: int,
        mail: fastapi_mail.FastMail,
        mail_sender: str,
    ):
        self.auth_store = auth_store
        self.users_store = users_store
        self.api_secret = api_secret
        self.key_size = key_size
        self.fernet = fernet
        self.jwt_ttl = jwt_ttl
        self.max_login_attempts = max_login_attempts
        self.mail = mail
        self.mail_sender = mail_sender
