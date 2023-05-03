"""Functionality for security"""
import uuid
from typing import Tuple, List, Optional

from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message

from api.errors import HTTPAuthenticationError


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Handles CSRF token geeneration and verification

    Thanks to https://github.com/gnat/csrf-starlette-fastapi
    CSRF / Cross Site Request Forgery Security Middleware for Starlette and FastAPI.
            1. Add this middleware using the middleware= parameter of your app.
            2. request.state.csrftoken will now be available.
            3. Use directly in an HTML <form> POST with <input type="hidden" name="csrftoken" value="{{ csrftoken }}" />
            4. Use with javascript / ajax POST by sending a request header 'csrftoken' with request.state.csrftoken
    Notes
            Users must should start on a "safe page" (a typical GET request) to generate the initial CSRF cookie.
            Uses session level CSRF so you can use frameworks such as htmx, without issues. (https://htmx.org/)
            Token is stored in request.state.csrftoken for use in templates.
    Reference
            https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

    License
        BSD 3-Clause License

        Copyright (c) 2022, Nathaniel Sabanski
        All rights reserved.

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice, this
           list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright notice,
           this list of conditions and the following disclaimer in the documentation
           and/or other materials provided with the distribution.

        3. Neither the name of the copyright holder nor the names of its
           contributors may be used to endorse or promote products derived from
           this software without specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """

    def __init__(
        self,
        app: ASGIApp,
        csrf_token_name: str = "csrftoken",
        csrf_token_expiry: int = (10 * 24 * 60 * 60),
        excluded_paths: Tuple[str, ...] = (),
    ):
        super().__init__(app)
        self._csrf_token_name = csrf_token_name
        self._csrf_token_expiry = csrf_token_expiry
        self._excluded_paths = {k: True for k in excluded_paths}

    @staticmethod
    async def set_body(request):
        """Read the body without consuming it
        https://github.com/encode/starlette/issues/495
        """
        receive_ = await request.receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.csrftoken = (
            ""  # Always available even if we don't get it from cookie.
        )

        token_new_cookie = False
        token_from_cookie = request.cookies.get(self._csrf_token_name, None)
        token_from_header = request.headers.get(self._csrf_token_name, None)

        if str(request.url.path) in self._excluded_paths:
            return await call_next(request)
        # 🍪 Fetch the cookie only if we're using an appropriate request method (like Django does).
        elif request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            await self.set_body(request)
            async with request.form() as form:
                token_from_form = form.get(self._csrf_token_name, None)

            if (
                not token_from_cookie or len(token_from_cookie) < 30
            ):  # Sanity check. UUID always > 30.
                raise HTTPAuthenticationError(detail="No CSRF cookie set!")
                # return PlainTextResponse(
                #     "No CSRF cookie set!", status_code=403
                # )  # 🔴 Fail check.
            if (str(token_from_cookie) != str(token_from_form)) and (
                str(token_from_cookie) != str(token_from_header)
            ):
                raise HTTPAuthenticationError(detail="CSRF cookie does not match!")
        else:
            # 🍪 Generates the cookie if one does not exist.
            # Has to be the same token throughout session! NOT a nonce.
            # 	"if you record a nonce value everytime I load a form and
            # 	then I can't go back to a different tab and submit that first form I will dislike your site."
            if not token_from_cookie:
                token_from_cookie = str(uuid.uuid4())
                token_new_cookie = True

        # 🟢 All good. Pass csrftoken up to controllers, templates.
        request.state.csrftoken = token_from_cookie

        # ⏰ Wait for response to happen.
        response = await call_next(request)

        # 🍪 Set CSRF cookie on the response.
        if token_new_cookie and token_from_cookie:
            response.set_cookie(
                self._csrf_token_name,
                token_from_cookie,
                self._csrf_token_expiry,
                path="/",
                domain=None,
                secure=False,
                httponly=False,
                samesite="strict",
            )

        return response


class OAuth2BearerScheme(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = "bearer",
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __get_multiple_tokens(self, request: Request) -> List[str]:
        """Retrieves the tokens from the header, cookie etc as a list"""
        tokens = []
        possible_locations = ["headers", "cookies"]

        for location in possible_locations:
            auth = getattr(request, location).get("Authorization")
            if auth:
                scheme, param = get_authorization_scheme_param(auth)
                if scheme.lower() == self.scheme_name:
                    tokens.append(param)

        return tokens

    async def __call__(self, request: Request) -> Optional[str]:
        tokens = await self.__get_multiple_tokens(request)
        if len(tokens) < 1:
            if self.auto_error:
                raise HTTPAuthenticationError()
            else:
                return None

        return tokens[0]
