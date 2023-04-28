from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from api.apps.admin.utils import templates
from api.errors import HTTPAuthenticationError
from api.utils import to_http_exception_with_link


async def redirect_unauthenticated_to_login(
    request: Request, exc: HTTPAuthenticationError
) -> Response:
    return RedirectResponse(url=request.url_for("login"))


async def redirect_to_error_page(request: Request, exc: Exception) -> Response:
    http_exc = to_http_exception_with_link(exc)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "detail": http_exc.detail,
            "helpful_link": http_exc.helpful_link,
        },
        status_code=http_exc.status_code,
    )
