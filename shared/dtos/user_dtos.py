from pydantic import BaseModel


class UserLoginDto(BaseModel):
    login: str
    password: str

class UserRegisterDto(BaseModel):
    login: str
    password: str

class UserDto(BaseModel):
    id: int
    name: str
    login: str
    experience: int
    gold: int