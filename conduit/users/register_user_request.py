from dataclasses import dataclass


@dataclass
class RegisterUserRequestUser:
    email: str
    password: str
    username: str


@dataclass
class RegisterUserRequest:
    user: RegisterUserRequestUser
