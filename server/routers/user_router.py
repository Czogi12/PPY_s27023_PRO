from fastapi import APIRouter

from dtos.user_dtos import UserLoginDto, UserRegisterDto
from ..services.user_service import UserService
def create_user_router(service: UserService) -> APIRouter:
    router = APIRouter(prefix="/users")

    @router.post("/login")
    def get_user(user: UserLoginDto):
        token = service.login(user.login, user.password)
        if token is None:
            return {"message": "Login failed"}, 401
        return {token: token}, 200

    @router.post("/")
    def get_user(user: UserRegisterDto):
        return user

    return router