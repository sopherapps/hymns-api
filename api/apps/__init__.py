"""The RESTful API and the admin site
"""
import gc

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

import settings
from services import hymns, auth, config
from services.store import Store

from .admin import admin_site
from .public import public_api


app = FastAPI()

# app set up
app.mount("/api", public_api)
app.mount("/admin", admin_site)


@app.on_event("startup")
async def start():
    """Initializes the hymns service"""
    settings.initialize()

    hymns_db_uri = settings.get_hymns_db_uri()
    auth_db_uri = settings.get_auth_db_uri()
    config_db_uri = settings.get_config_db_uri()
    hymns_service_conf = settings.get_hymns_service_config()
    api_key_length = settings.get_api_key_length()
    api_secret = settings.get_api_secret()
    jwt_ttl = settings.get_jwt_ttl_in_sec()
    max_login_attempts = settings.get_max_login_attempts()
    mail_config = settings.get_email_config()
    mail_sender = settings.get_auth_email_sender()
    otp_verification_url = settings.get_otp_verification_url()

    await config.save_service_config(config_db_uri, hymns_service_conf)

    global admin_site

    # hymns service
    hymns_service = await hymns.initialize(
        config_db_uri=config_db_uri, service_db_uri=hymns_db_uri
    )
    app.state.hymns_service = hymns_service
    admin_site.state.hymns_service = hymns_service
    public_api.state.hymns_service = hymns_service

    # auth service
    auth_service = await auth.initialize(
        config_db_uri=config_db_uri,
        service_db_uri=auth_db_uri,
        key_size=api_key_length,
        api_secret=api_secret,
        jwt_ttl=jwt_ttl,
        max_login_attempts=max_login_attempts,
        mail_config=mail_config,
        mail_sender=mail_sender,
    )
    app.state.auth_service = auth_service
    admin_site.state.auth_service = auth_service
    public_api.state.auth_service = auth_service
    admin_site.state.otp_verification_url = otp_verification_url

    # API limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.get_rate_limit()],
        enabled=settings.get_is_rate_limit_enabled(),
    )
    app.state.limiter = limiter
    public_api.state.limiter = limiter
    admin_site.state.limiter = limiter


@app.on_event("shutdown")
async def shutdown():
    """Shuts down the application"""
    # Shut down all stores
    await Store.destroy_stores()
    gc.collect()
