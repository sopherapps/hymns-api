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
    token_type: str = "bearer"
    message: str


class OTPResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    """The request sent when attempting to change the password"""

    original_password: str
    new_password: str
    username: str
