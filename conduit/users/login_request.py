from dataclasses import dataclass


@dataclass
class LoginRequestUser:
    email: str
    password: str


@dataclass
class LoginRequest:
    user: LoginRequestUser
