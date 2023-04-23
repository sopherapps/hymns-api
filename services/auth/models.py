from pydantic import BaseModel


class UserDTO(BaseModel):
    username: str
    email: str
    password: str

    @classmethod
    def from_user_in_db(cls, user: "UserInDb") -> "UserDTO":
        return UserDTO(username=user.username, email=user.email, password=user.password)


class UserInDb(BaseModel):
    username: str
    email: str  # encrypted
    password: str  # hashed
    otp_counter: str  # encrypted
    otp_secret: str  # encrypted
    login_attempts: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    message: str


class OTPResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class ChangePasswordRequest(BaseModel):
    """The request sent when attempting to change the password"""

    original_password: str
    new_password: str
    username: str


class Application(BaseModel):
    """An application registered to interface with the API

    Intentionally have no data associated with an application
    such that in case of a breach, no client data is at risk.
    Otherwise we would have used a Oauth2: say a request sent
    to a login link with API key and client secret, then a JWT
    access token to be used per request is generated and returned
    to client.
    """

    key: str
