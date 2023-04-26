"""Common state of the admin app"""
from fastapi import FastAPI
from starlette.templating import Jinja2Templates

import settings
from api.auth import BearerTokenAuthBackend

admin_site = FastAPI(root_path="/admin")
oauth2_backend = BearerTokenAuthBackend(login_url="/admin/login")
cookie_ttl: int = 1800
templates = Jinja2Templates(directory=settings.get_templates_folder())
