from dataclasses import dataclass


@dataclass
class RegisterUserRequestUser:
    username: str
    email: str
    password: str


@dataclass
class RegisterUserRequest:
    user: RegisterUserRequestUser
