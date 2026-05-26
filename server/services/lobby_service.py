import random
from typing import Optional

import socketio

from shared.models.lobby import Lobby, MAX_USERS
from shared.models.user import User


def _room(lobby_id: int) -> str:
    return f"lobby:{lobby_id}"


class LobbyError(Exception):
    pass


class LobbyService:
    def __init__(self, sio: socketio.AsyncServer) -> None:
        self.sio = sio
        self._lobbies: dict[int, Lobby] = {}
        self._user_lobby: dict[int, int] = {}
        self._next_id: int = 1

    def list(self) -> list[Lobby]:
        return list(self._lobbies.values())

    def get(self, lobby_id: int) -> Optional[Lobby]:
        return self._lobbies.get(lobby_id)

    def get_user_lobby(self, user_id: int) -> Optional[Lobby]:
        lobby_id = self._user_lobby.get(user_id)
        if lobby_id is None:
            return None
        return self._lobbies.get(lobby_id)

    async def create(self, host: User, name: str) -> Lobby:
        if host.id in self._user_lobby:
            raise LobbyError("User already in a lobby")
        lobby = Lobby(self._next_id, name, host)
        self._next_id += 1
        self._lobbies[lobby.id] = lobby
        self._user_lobby[host.id] = lobby.id
        return lobby

    async def join(self, user: User, lobby_id: int) -> Lobby:
        if user.id in self._user_lobby:
            raise LobbyError("User already in a lobby")
        lobby = self._lobbies.get(lobby_id)
        if lobby is None:
            raise LobbyError("Lobby not found")
        if len(lobby.users) >= MAX_USERS:
            raise LobbyError("Lobby is full")
        lobby.users.append(user)
        self._user_lobby[user.id] = lobby.id
        await self._emit_user_joined(lobby, user)
        await self._emit_lobby_updated(lobby)
        return lobby

    async def leave(self, user: User) -> Optional[Lobby]:
        lobby_id = self._user_lobby.pop(user.id, None)
        if lobby_id is None:
            return None
        lobby = self._lobbies.get(lobby_id)
        if lobby is None:
            return None
        lobby.users = [u for u in lobby.users if u.id != user.id]
        await self._emit_user_left(lobby, user)
        if not lobby.users:
            await self._dissolve(lobby)
            return None
        if lobby.host.id == user.id:
            lobby.host = random.choice(lobby.users)
        await self._emit_lobby_updated(lobby)
        return lobby

    async def delete(self, user: User, lobby_id: int) -> None:
        lobby = self._lobbies.get(lobby_id)
        if lobby is None:
            raise LobbyError("Lobby not found")
        if lobby.host.id != user.id:
            raise LobbyError("Only host can delete the lobby")
        await self._dissolve(lobby)

    async def _dissolve(self, lobby: Lobby) -> None:
        for u in lobby.users:
            self._user_lobby.pop(u.id, None)
        self._lobbies.pop(lobby.id, None)
        await self._emit_lobby_closed(lobby)
        await self.sio.close_room(_room(lobby.id))

    async def _emit_user_joined(self, lobby: Lobby, user: User) -> None:
        await self.sio.emit(
            "user_joined",
            {"user_id": user.id, "name": user.name},
            room=_room(lobby.id),
        )

    async def _emit_user_left(self, lobby: Lobby, user: User) -> None:
        await self.sio.emit(
            "user_left",
            {"user_id": user.id},
            room=_room(lobby.id),
        )

    async def _emit_lobby_updated(self, lobby: Lobby) -> None:
        await self.sio.emit(
            "lobby_updated",
            self._lobby_payload(lobby),
            room=_room(lobby.id),
        )

    async def _emit_lobby_closed(self, lobby: Lobby) -> None:
        await self.sio.emit(
            "lobby_closed",
            {"lobby_id": lobby.id},
            room=_room(lobby.id),
        )

    @staticmethod
    def _lobby_payload(lobby: Lobby) -> dict:
        return {
            "id": lobby.id,
            "name": lobby.name,
            "host_id": lobby.host.id,
            "users": [
                {"id": u.id, "name": u.name}
                for u in lobby.users
            ],
        }
