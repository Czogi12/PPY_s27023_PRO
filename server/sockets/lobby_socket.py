import socketio

from ..services.lobby_service import LobbyService
from ..services.user_service import UserService


def _room(lobby_id: int) -> str:
    return f"lobby:{lobby_id}"


def register_lobby_socket(
    sio: socketio.AsyncServer,
    lobby_service: LobbyService,
    user_service: UserService,
) -> None:
    @sio.event
    async def connect(sid, environ, auth):
        token = (auth or {}).get("token") if isinstance(auth, dict) else None
        if not token:
            raise socketio.exceptions.ConnectionRefusedError("Missing token")
        user = user_service.get_by_token(token)
        if user is None:
            raise socketio.exceptions.ConnectionRefusedError("Invalid token")
        lobby = lobby_service.get_user_lobby(user.id)
        if lobby is None:
            raise socketio.exceptions.ConnectionRefusedError("User not in any lobby")
        await sio.save_session(sid, {"user_id": user.id, "lobby_id": lobby.id})
        await sio.enter_room(sid, _room(lobby.id))

    @sio.event
    async def disconnect(sid):
        session = await sio.get_session(sid)
        user_id = session.get("user_id") if session else None
        if user_id is None:
            return
        lobby = lobby_service.get_user_lobby(user_id)
        if lobby is None:
            return
        user = next((u for u in lobby.users if u.id == user_id), None)
        if user is None:
            return
        await lobby_service.leave(user)
