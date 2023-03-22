import random
import string
from datetime import timedelta, datetime
from typing import Any

from cryptography.fernet import Fernet
from jose import jwt, JWTError
from passlib.context import CryptContext

from services.auth.errors import AuthenticationError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_key(size: int) -> str:
    """Generates a random key of given size

    Args:
        size: the number of digits the key is to have.

    Returns:
        the generated key
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(size))


def encrypt_str(fernet: Fernet, word: str) -> str:
    """Encrypts the word and returns the result

    Args:
        fernet: the Fernet for encrypting and decrypting values
        word: the email to encrypt

    Returns:
        the encrypted word
    """
    value = fernet.encrypt(word.encode())
    return value.decode()


def decrypt_str(fernet: Fernet, word) -> str:
    """Decrypts a given word

    Args:
        fernet: the Fernet for encrypting and decrypting values
        word: the email to decrypt

    Returns:
        the decrypted word
    """
    value = fernet.decrypt(word)
    return value.decode()


def hash_password(password: str) -> str:
    """Hashes the given password and returns the hash

    Args:
        password: the password to hash

    Returns:
        the hashed password
    """
    return _pwd_context.hash(password)


def is_password_match(raw_password: str, hashed_password: str) -> bool:
    """Verifies whether the hashed_password is a hash of the password.

    Args:
        raw_password: the raw password
        hashed_password: the hash of the password

    Returns:
        a boolean True if the two match, else False
    """
    return _pwd_context.verify(raw_password, hashed_password)


def generate_access_token(
    _id: str, secret_key: str, ttl: timedelta, algorithm: str, **claims
) -> str:
    """Generates a JWT access token wrapping the given data, and having the given time-to-live

    Ideally the _id will be encrypted to hide it from any prying eyes.

    Args:
        _id: the encrypted unique identifier for the user associated with this access token
        secret_key: the secret key used to JWT encrypt the payload
        ttl: the timedelta for which the given token is to live for before expiring
        algorithm: the cryptographic algorithm used to encrypt the token
        claims: the extra claims to attach to the access token. Ensure that no private data is added here.

    Returns:
        the JWT
    """
    payload = {**claims, "sub": _id, "exp": datetime.utcnow() + ttl}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_jwt(token: str, secret_key: str, algorithm: str) -> Any:
    """Extracts the payload that is found in the JWT

    Args:
        token: the jwt token to decode
        secret_key: the secret key used to JWT encrypt the payload
        algorithm: the cryptographic algorithm used to encrypt the token

    Returns:
        the Dict representation of the claims set in the JWT token

    Raises:
        AuthenticationError: if subject in token is None or there is a JWT Error
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        _id: str = payload.get("sub")
        if _id is None:
            raise AuthenticationError("invalid token")

        return payload
    except JWTError:
        raise AuthenticationError("invalid token")
