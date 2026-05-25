from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable

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
        self.http = httpx.Client(base_url=server_url, timeout=5.0)
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._pending: list[tuple[Future, Callable]] = []
        self.change_scene(LoginScene)

    def change_scene(self, scene_cls, **kwargs) -> None:
        if self.scene is not None:
            self.scene.on_exit()
        self.scene = scene_cls(self, self.screen, **kwargs)
        self.scene.on_enter()

    def tick(self) -> None:
        """Drain completed async results onto the main thread."""
        still: list[tuple[Future, Callable]] = []
        for fut, cb in self._pending:
            if fut.done():
                try:
                    result = fut.result()
                except Exception as e:
                    result = (None, f"{e}")
                try:
                    cb(result)
                except Exception as e:
                    print(f"async callback error: {e}")
            else:
                still.append((fut, cb))
        self._pending = still

    def submit(self, func: Callable, *args, on_done: Callable, **kwargs) -> None:
        fut = self._executor.submit(func, *args, **kwargs)
        self._pending.append((fut, on_done))

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def login(self, login: str, password: str) -> tuple[str | None, str | None]:
        try:
            resp = self.http.post("/users/login", json={"login": login, "password": password})
        except Exception as e:
            return None, f"Network error: {e}"
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"

    def register(self, login: str, password: str) -> tuple[bool, str | None]:
        try:
            resp = self.http.post("/users/register", json={"login": login, "password": password})
        except Exception as e:
            return False, f"Network error: {e}"
        if resp.status_code == 201:
            return True, None
        return False, f"HTTP {resp.status_code}"

    def fetch_me(self) -> tuple[dict | None, str | None]:
        if self.token is None:
            return None, "Not authenticated"
        try:
            resp = self.http.get("/users/me", headers=self._auth_headers())
        except Exception as e:
            return None, f"Network error: {e}"
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"

    def fetch_lobbies(self) -> tuple[list[dict] | None, str | None]:
        if self.token is None:
            return None, "Not authenticated"
        try:
            resp = self.http.get("/lobbies", headers=self._auth_headers())
        except Exception as e:
            return None, f"Network error: {e}"
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"

    def create_lobby(self, name: str) -> tuple[dict | None, str | None]:
        return self._lobby_request("POST", "/lobbies", json={"name": name}, ok=201)

    def fetch_lobby(self, lobby_id: int) -> tuple[dict | None, str | None]:
        return self._lobby_request("GET", f"/lobbies/{lobby_id}", ok=200)

    def join_lobby(self, lobby_id: int) -> tuple[dict | None, str | None]:
        return self._lobby_request("POST", f"/lobbies/{lobby_id}/join", ok=200)

    def leave_lobby(self, lobby_id: int) -> tuple[None, str | None]:
        return self._lobby_request("POST", f"/lobbies/{lobby_id}/leave", ok=204)

    def delete_lobby(self, lobby_id: int) -> tuple[None, str | None]:
        return self._lobby_request("DELETE", f"/lobbies/{lobby_id}", ok=204)

    def _lobby_request(self, method: str, path: str, ok: int, json=None):
        if self.token is None:
            return None, "Not authenticated"
        try:
            resp = self.http.request(method, path, json=json, headers=self._auth_headers())
        except Exception as e:
            return None, f"Network error: {e}"
        if resp.status_code == ok:
            if resp.status_code == 204 or not resp.content:
                return None, None
            return resp.json(), None
        try:
            detail = resp.json().get("detail")
        except Exception:
            detail = None
        return None, detail or f"HTTP {resp.status_code}"
