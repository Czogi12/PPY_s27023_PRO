import httpx

from .models.user import User
from .scenes.login_scene import LoginScene


class App:
    def __init__(self, screen, server_url: str) -> None:
        self.screen = screen
        self.server_url = server_url
        self.user: User | None = None
        self.token: str | None = None
        self.scene = None
        self.change_scene(LoginScene)

    def change_scene(self, scene_cls, **kwargs) -> None:
        if self.scene is not None:
            self.scene.on_exit()
        self.scene = scene_cls(self, self.screen, **kwargs)
        self.scene.on_enter()

    def login(self, login, password) -> bool:
        resp = httpx.post(f"{self.server_url}/users/login", json={
        "login": login, "password": password
        })
        if resp.status_code == 200:
            self.token = resp.json()
            return True
        return False
    def register(self, login, password) -> bool:
        resp = httpx.post(f"{self.server_url}/users/register", json={
            "login": login, "password": password
        })
        return resp.status_code == 201

    def fetch_me(self) -> bool:
        if self.user is not None:
            return True
        if self.token is None:
            return False
        resp = httpx.get(
            f"{self.server_url}/users/me",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if resp.status_code != 200:
            return False
        data = resp.json()
        self.user = User(password_hash="", **data)
        return True

