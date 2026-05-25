from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dtos.user_dtos import UserDto, UserLoginDto, UserRegisterDto
from ..services.user_service import UserService

_security = HTTPBearer()


def create_user_router(service: UserService) -> APIRouter:
    router = APIRouter(prefix="/users")

    @router.post("/login")
    def login(user: UserLoginDto):
        token = service.login(user.login, user.password)
        if token is None:
            raise HTTPException(status_code=401, detail="Login failed")
        return token

    @router.post("/register", status_code=201)
    def register(user: UserRegisterDto):
        if not service.register(user.login, user.password):
            raise HTTPException(status_code=409, detail="User already exists")
        return {"ok": True}

    @router.get("/me", response_model=UserDto)
    def get_me(credentials: HTTPAuthorizationCredentials = Depends(_security)):
        user = service.get_by_token(credentials.credentials)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UserDto(
            id=user.id,
            name=user.name,
            login=user.login,
            experience=user.experience,
            gold=user.gold,
        )

    return router
