"""All types for the auth service"""
import fastapi_mail
import funml as ml
from cryptography.fernet import Fernet
from py_scdb import AsyncStore


@ml.record
class AuthService:
    auth_store: AsyncStore
    users_store: AsyncStore
    api_secret: str
    key_size: int
    fernet: Fernet
    jwt_ttl: float
    max_login_attempts: int
    mail: fastapi_mail.FastMail
    mail_sender: str


@ml.record
class Application:
    """An application registered to interface with the API

    Intentionally have no data associated with an application
    such that in case of a breach, no client data is at risk.
    Otherwise we would have used a Oauth2: say a request sent
    to a login link with API key and client secret, then a JWT
    access token to be used per request is generated and returned
    to client.
    """

    key: str
