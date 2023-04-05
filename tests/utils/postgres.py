import asyncpg
import pyotp
from cryptography.fernet import Fernet
from sqlalchemy import make_url

from services.auth.models import UserDTO
from services.auth.utils import encrypt_str, hash_password


async def create_pg_db_if_not_exists(db_uri: str):
    """Creates a postgres database if not exists

    Args:
        db_uri: the postgres database url to connect to
    """
    try:
        conn = await asyncpg.connect(dsn=db_uri)
        await conn.close()
    except asyncpg.InvalidCatalogNameError:
        # Database does not exist, create it.
        uri = make_url(db_uri)
        sys_password = uri.password if uri.username == "postgres" else None
        sys_conn = await asyncpg.connect(
            database="template1",
            user="postgres",
            host=uri.host,
            password=sys_password,
        )

        try:
            await sys_conn.execute(
                f"CREATE DATABASE {uri.database} OWNER {uri.username}"
            )
        finally:
            await sys_conn.close()


async def drop_pg_db_if_exists(db_uri: str):
    """Creates a postgres database if not exists

    Args:
        db_uri: the postgres database url to connect to
    """
    uri = make_url(db_uri)
    sys_password = uri.password if uri.username == "postgres" else None
    sys_conn = await asyncpg.connect(
        database="template1",
        user="postgres",
        host=uri.host,
        password=sys_password,
    )
    try:
        await sys_conn.execute(f"DROP DATABASE IF EXISTS {uri.database}")
    finally:
        await sys_conn.close()


async def delete_pg_table(db_uri: str, table: str):
    """Drops a given table if exists

    Args:
        db_uri: the postgres database url to connect to
        table: the table to delete
    """
    conn = await asyncpg.connect(db_uri)
    try:
        await conn.execute(f"DROP TABLE IF EXISTS {table}")
    finally:
        await conn.close()


async def create_pg_user_table(db_uri: str):
    """Creates the `users` table in postgres if not exists

    Args:
        db_uri: the postgres database url to connect to
    """
    conn = await asyncpg.connect(db_uri)
    try:
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS public.users (
            "username" varchar (255) NOT NULL,
            "email" varchar (255) NOT NULL,
            "password" varchar (255) NOT NULL,
            "otp_counter" varchar (255),
            "otp_secret" varchar (255),
            "login_attempts" integer default 0,
             CONSTRAINT users_pkey PRIMARY KEY (username)
        )
        """
        )
    finally:
        await conn.close()


async def pg_upsert_user(db_uri: str, fernet: Fernet, user: UserDTO):
    """Upsert a user into the database at the database URI"""
    conn = await asyncpg.connect(db_uri)

    try:
        await conn.execute(
            f"""
            INSERT INTO public.users (
                "username",
                "email",
                "password",
                "otp_counter",
                "otp_secret",
                "login_attempts"
            ) VALUES (
                '{user.username}',
                '{encrypt_str(fernet, user.email)}',
                '{hash_password(user.password)}',
                '{encrypt_str(fernet, "0")}',
                '{encrypt_str(fernet, pyotp.random_base32())}',
                0
            ) ON CONFLICT ON CONSTRAINT users_pkey
            DO
                UPDATE SET 
                    email = EXCLUDED.email,
                    password = EXCLUDED.password,
                    otp_counter = EXCLUDED.otp_counter,
                    otp_secret = EXCLUDED.otp_secret,
                    login_attempts = EXCLUDED.login_attempts      
        """
        )
    finally:
        await conn.close()


async def pg_table_exists(db_uri: str, table: str) -> bool:
    """Checks to see a given postgres table exists

    Args:
        db_uri: the postgres database url to connect to
        table: the table to check for

    Returns:
        whether the postgres table exists
    """
    conn = await asyncpg.connect(db_uri)
    try:
        exists = await conn.fetchval(
            f"""SELECT EXISTS (
                    SELECT FROM 
                        pg_tables
                    WHERE 
                        schemaname = 'public' AND 
                        tablename  = '{table}'
                    )
            """
        )
    finally:
        await conn.close()

    return exists
