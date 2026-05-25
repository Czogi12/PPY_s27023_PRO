from models.user import User


MAX_USERS = 20


class Lobby:
    def __init__(self, id: int, name: str, host: User) -> None:
        self.id: int = id
        self.name: str = name
        self.host: User = host
        self.users: list[User] = [host]
