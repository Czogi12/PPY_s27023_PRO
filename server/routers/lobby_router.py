from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.dtos.lobby_dtos import LobbyCreateDto, LobbyDto, LobbySummaryDto
from shared.dtos.user_dtos import UserDto
from shared.models.lobby import Lobby
from ..services.lobby_service import LobbyError, LobbyService
from ..services.user_service import UserService

_security = HTTPBearer()


def _to_dto(lobby: Lobby) -> LobbyDto:
    return LobbyDto(
        id=lobby.id,
        name=lobby.name,
        host_id=lobby.host.id,
        users=[
            UserDto(
                id=u.id,
                name=u.name,
                login=u.login,
                experience=u.experience,
                gold=u.gold,
            )
            for u in lobby.users
        ],
    )


def _to_summary(lobby: Lobby) -> LobbySummaryDto:
    return LobbySummaryDto(
        id=lobby.id,
        name=lobby.name,
        host_id=lobby.host.id,
        user_count=len(lobby.users),
    )


def create_lobby_router(
    lobby_service: LobbyService,
    user_service: UserService,
) -> APIRouter:
    router = APIRouter(prefix="/lobbies")

    def _auth(credentials: HTTPAuthorizationCredentials = Depends(_security)):
        user = user_service.get_by_token(credentials.credentials)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user

    @router.get("", response_model=list[LobbySummaryDto])
    def list_lobbies(_=Depends(_auth)):
        return [_to_summary(l) for l in lobby_service.list()]

    @router.get("/{lobby_id}", response_model=LobbyDto)
    def get_lobby(lobby_id: int, _=Depends(_auth)):
        lobby = lobby_service.get(lobby_id)
        if lobby is None:
            raise HTTPException(status_code=404, detail="Lobby not found")
        return _to_dto(lobby)

    @router.post("", response_model=LobbyDto, status_code=201)
    async def create_lobby(payload: LobbyCreateDto, user=Depends(_auth)):
        try:
            lobby = await lobby_service.create(user, payload.name)
        except LobbyError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return _to_dto(lobby)

    @router.post("/{lobby_id}/join", response_model=LobbyDto)
    async def join_lobby(lobby_id: int, user=Depends(_auth)):
        try:
            lobby = await lobby_service.join(user, lobby_id)
        except LobbyError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return _to_dto(lobby)

    @router.post("/{lobby_id}/leave", status_code=204)
    async def leave_lobby(lobby_id: int, user=Depends(_auth)):
        current = lobby_service.get_user_lobby(user.id)
        if current is None or current.id != lobby_id:
            raise HTTPException(status_code=409, detail="User not in this lobby")
        await lobby_service.leave(user)

    @router.delete("/{lobby_id}", status_code=204)
    async def delete_lobby(lobby_id: int, user=Depends(_auth)):
        try:
            await lobby_service.delete(user, lobby_id)
        except LobbyError as e:
            status = 404 if "not found" in str(e).lower() else 403
            raise HTTPException(status_code=status, detail=str(e))

    return router
