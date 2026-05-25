import hmac
import hashlib
import json
import os

from models.user import User


_DEFAULT_DATA_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.json"))


class UserService:
    def __init__(self, salt, hash_key, data_file=_DEFAULT_DATA_FILE):
        self.users: list[User] = list()
        self.sessions = {}
        self.salt = salt
        self.hash_key = hash_key
        self.data_file = data_file
        self.__deserialize()

    def login(self, login, password):
        print(login, password)
        user = self.__get_user(login, password)
        if user is None:
            return False
        self.sessions = {
            token: u for token, u in self.sessions.items()
            if u.login != user.login
        }
        token = os.urandom(32).hex()
        self.sessions[token] = user
        return token
    def get_by_token(self, token):
        return self.sessions.get(token)

    def register(self, login, password):
        if self.__get_user_by_login(login) is not None:
            return False
        id = len(self.users) + 1
        user = User(id, f"Użytkownik {id}", login, self.__hash_password(password), 0, 0)
        self.users.append(user)
        self.__serialize()
        return True

    def __serialize(self):
        data = [
            {
                "id": u.id,
                "name": u.name,
                "login": u.login,
                "password_hash": u.password_hash,
                "experience": u.experience,
                "gold": u.gold,
            }
            for u in self.users
        ]
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def __deserialize(self):
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.users = [
            User(u["id"], u["name"], u["login"], u["password_hash"], u["experience"], u["gold"])
            for u in data
        ]

    def __get_user(self, login, password):
        psw_hash = self.__hash_password(password)
        for user in self.users:
            if user.login == login and user.password_hash == psw_hash:
                return user
        return None

    def __get_user_by_login(self, login):
        for user in self.users:
            if user.login == login:
                return user
        return None

    def __hash_password(self, password: str) -> str:
        return hmac.new(
            self.hash_key.encode(),
            (self.salt + password).encode(),
            hashlib.sha256
        ).hexdigest()
