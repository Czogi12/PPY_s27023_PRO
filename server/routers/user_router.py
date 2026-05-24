from fastapi import APIRouter

from dtos.user_dtos import UserLoginDto, UserRegisterDto
from ..services.user_service import UserService

router = APIRouter(prefix="/users")
service = UserService()

@router.get("/")
def get_user(user: UserLoginDto):
    return user

@router.post("/")
def get_user(user: UserRegisterDto):
    return user