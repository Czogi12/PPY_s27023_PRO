import httpx

from models.user import User
from .scenes.login_scene import LoginScene


class App:
    def __init__(self, screen, server_url: str) -> None:
        self.screen = screen
        self.server_url = server_url
        self.scene = LoginScene(self, screen)
        self.user: User | None = None
        pass
    def login(self, login, password) -> bool:
        resp = httpx.post(f"{self.server_url}/users/login", json={
        "login": login, "password": password
        })
        print(resp.json())
        return True

