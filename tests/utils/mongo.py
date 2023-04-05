import pymongo
import pyotp
from cryptography.fernet import Fernet

from services.auth.models import UserDTO
from services.auth.utils import encrypt_str, hash_password


def clear_mongo_db(uri: str):
    """Clears the database at the given URI

    Args:
        uri: the URI of the mongodb server
    """
    db = pymongo.MongoClient(uri)
    for db_name in db.list_database_names():
        try:
            db.drop_database(db_name)
        except pymongo.errors.OperationFailure as exp:
            if "dropping the 'admin' database is prohibited" not in f"{exp}".lower():
                raise exp


def mongo_upsert_user(db_uri: str, fernet: Fernet, user: UserDTO):
    """Upsert a user into the mongo database at the database URI"""
    client = pymongo.MongoClient(db_uri)

    try:
        data = dict(
            username=f"{user.username}",
            email=f"{encrypt_str(fernet, user.email)}",
            password=f"{hash_password(user.password)}",
            otp_counter=f'{encrypt_str(fernet, "0")}',
            otp_secret=f"{encrypt_str(fernet, pyotp.random_base32())}",
            login_attempts=0,
        )
        client["data"]["users"].update_one(
            filter={"username": user.username}, update={"$set": data}, upsert=True
        )
    finally:
        client.close()
