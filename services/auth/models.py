import funml as ml


@ml.record
class UserDTO:
    username: str
    email: str
    password: str

    @classmethod
    def from_user_in_db(cls, user: "UserInDb") -> "UserDTO":
        return UserDTO(username=user.username, email=user.email, password=user.password)


@ml.record
class UserInDb:
    username: str
    email: str  # encrypted
    password: str  # hashed
    otp_counter: str  # encrypted
    otp_secret: str  # encrypted
    login_attempts: int


@ml.record
class LoginResponse:
    token: str
    message: str


@ml.record
class OTPResponse:
    token: str


@ml.record
class ChangePasswordRequest:
    """The request sent when attempting to change the password"""

    original_password: str
    new_password: str
    username: str
