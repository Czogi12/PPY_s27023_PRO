from pydantic import BaseModel


class UserLoginDto(BaseModel):
    login: str
    password: str

class UserRegisterDto(BaseModel):
    login: str
    password: str