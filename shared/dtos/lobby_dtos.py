from pydantic import BaseModel

from .user_dtos import UserDto


class LobbyCreateDto(BaseModel):
    name: str


class LobbySummaryDto(BaseModel):
    id: int
    name: str
    host_id: int
    user_count: int


class LobbyDto(BaseModel):
    id: int
    name: str
    host_id: int
    users: list[UserDto]
