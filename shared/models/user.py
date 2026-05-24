class User:
    def __init__(self) -> None:
        self.id: int
        self.name: str
        self.login: str
        self.password_hash: str
        self.experience: int
        self.gold: int