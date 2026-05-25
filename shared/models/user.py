class User:
    def __init__(self, id, name, login, password_hash, experience, gold) -> None:
        self.id: int = id
        self.name: str = name
        self.login: str = login
        self.password_hash: str = password_hash
        self.experience: int = experience
        self.gold: int = gold