import hmac
import hashlib
import os

from models.user import User


class UserService:
    def __init__(self, salt, hash_key):
        from models.user import User
        self.users: [User] = []
        self.sessions = {}
        self.salt = salt
        self.hash_key = hash_key

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
    def register(self, login, password):
        user = self.__get_user(login, password)
        if user is not None:
            return False
        id = len(self.users) + 1
        user = User(id, f"Użytkownik {id}", login, self.hash_password(password), 0, 0)
        self.users.append(user)
        return True

    def __get_user(self, login, password):
        psw_hash = self.hash_password(password)
        for user in self.users:
            if user.login == login and user.password_hash == psw_hash:
                return user
        return None

    def hash_password(self, password: str) -> str:
        return hmac.new(
            self.hash_key.encode(),
            (self.salt + password).encode(),
            hashlib.sha256
        ).hexdigest()
