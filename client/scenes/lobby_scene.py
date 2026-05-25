import queue

import pygame
import pygame_gui
import socketio

from .logged_scene import LoggedScene


_USER_ROW_H = 30


class LobbyScene(LoggedScene):
    def __init__(self, app, screen, lobby_id: int):
        super().__init__(app, screen)
        self.lobby_id = lobby_id
        self.lobby: dict | None = None
        self.sio: socketio.Client | None = None
        self._events: queue.Queue = queue.Queue()
        self._user_labels: list[pygame_gui.elements.UILabel] = []

        screen_w = screen.get_width()
        screen_h = screen.get_height()

        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 60, screen_w, 36),
            manager=self.ui,
            text="Lobby",
        )

        list_w = min(400, screen_w - 40)
        list_x = (screen_w - list_w) // 2
        self.players_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(list_x, 110, list_w, 24),
            manager=self.ui,
            text="Players",
        )
        self.scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(list_x, 140, list_w, 340),
            manager=self.ui,
        )

        btn_y = screen_h - 60
        btn_w = 140
        btn_h = 40
        self.leave_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(240, btn_y, btn_w, btn_h),
            manager=self.ui,
            text="Leave",
        )
        self.delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, btn_y, btn_w, btn_h),
            manager=self.ui,
            text="Delete",
        )
        self.delete_btn.hide()

    def on_enter(self) -> None:
        super().on_enter()
        self.app.submit(self.app.fetch_lobby, self.lobby_id, on_done=self._on_fetched)

    def on_exit(self) -> None:
        self._disconnect_socket()
        super().on_exit()

    def handle_content_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.leave_btn:
            self.__leave()
        elif event.ui_element == self.delete_btn:
            self.__delete()

    def update_content(self, dt: float) -> None:
        while self._alive:
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            self._handle_socket_event(event)

    def draw_content(self, surface: pygame.Surface) -> None:
        pass

    def _on_fetched(self, result) -> None:
        if not self._alive:
            return
        lobby, error = result
        if lobby is None:
            print(f"fetch_lobby failed: {error}")
            self._navigate_back()
            return
        self.lobby = lobby
        self._render_lobby()
        self._connect_socket()

    def _connect_socket(self) -> None:
        def worker():
            sio = socketio.Client()

            @sio.on("user_joined")
            def _on_user_joined(data):
                self._events.put(("user_joined", data))

            @sio.on("user_left")
            def _on_user_left(data):
                self._events.put(("user_left", data))

            @sio.on("lobby_updated")
            def _on_lobby_updated(data):
                self._events.put(("lobby_updated", data))

            @sio.on("lobby_closed")
            def _on_lobby_closed(data):
                self._events.put(("lobby_closed", data))

            try:
                sio.connect(
                    self.app.server_url,
                    auth={"token": self.app.token},
                    transports=["websocket"],
                    wait_timeout=3,
                )
                return sio, None
            except Exception as e:
                return None, str(e)

        self.app.submit(worker, on_done=self._on_socket_connected)

    def _on_socket_connected(self, result) -> None:
        sio, error = result
        if error is not None:
            print(f"socket connect failed: {error}")
            return
        if not self._alive:
            try:
                sio.disconnect()
            except Exception:
                pass
            return
        self.sio = sio

    def _disconnect_socket(self) -> None:
        if self.sio is None:
            return
        try:
            self.sio.disconnect()
        except Exception:
            pass
        self.sio = None

    def _handle_socket_event(self, event: tuple) -> None:
        kind, data = event
        if kind == "lobby_closed":
            self._navigate_back()
            return
        if self.lobby is None:
            return
        if kind == "lobby_updated":
            self.lobby = {**self.lobby, **data}
            self._render_lobby()
        elif kind == "user_joined":
            uid = data.get("user_id")
            if uid is None or any(u["id"] == uid for u in self.lobby["users"]):
                return
            self.lobby["users"].append({"id": uid, "name": data.get("name", "")})
            self._render_lobby()
        elif kind == "user_left":
            uid = data.get("user_id")
            self.lobby["users"] = [u for u in self.lobby["users"] if u["id"] != uid]
            self._render_lobby()

    def _render_lobby(self) -> None:
        if self.lobby is None:
            return
        self.name_label.set_text(self.lobby.get("name", ""))

        for label in self._user_labels:
            label.kill()
        self._user_labels.clear()

        inner_w = self.scroll.get_container().get_size()[0]
        host_id = self.lobby.get("host_id")
        for i, user in enumerate(self.lobby.get("users", [])):
            text = user.get("name", "")
            if user.get("id") == host_id:
                text += " (host)"
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, i * _USER_ROW_H, inner_w, _USER_ROW_H - 2),
                manager=self.ui,
                container=self.scroll,
                text=text,
            )
            self._user_labels.append(label)
        self.scroll.set_scrollable_area_dimensions(
            (inner_w, max(1, len(self._user_labels) * _USER_ROW_H))
        )

        if self._is_host():
            self.delete_btn.show()
        else:
            self.delete_btn.hide()

    def _is_host(self) -> bool:
        return (
            self.lobby is not None
            and self.app.user is not None
            and self.lobby.get("host_id") == self.app.user.id
        )

    def _navigate_back(self) -> None:
        if not self._alive:
            return
        from .browser_scene import BrowserScene
        self.app.change_scene(BrowserScene)

    def __leave(self) -> None:
        if not self._alive:
            return
        self.leave_btn.disable()
        self.delete_btn.disable()
        self.app.submit(self.app.leave_lobby, self.lobby_id, on_done=self._on_left)

    def _on_left(self, result) -> None:
        if not self._alive:
            return
        _, error = result
        if error is not None:
            print(f"leave failed: {error}")
            self.leave_btn.enable()
            if self._is_host():
                self.delete_btn.enable()
            return
        self._navigate_back()

    def __delete(self) -> None:
        if not self._alive:
            return
        self.leave_btn.disable()
        self.delete_btn.disable()
        self.app.submit(self.app.delete_lobby, self.lobby_id, on_done=self._on_deleted)

    def _on_deleted(self, result) -> None:
        if not self._alive:
            return
        _, error = result
        if error is not None:
            print(f"delete failed: {error}")
            self.leave_btn.enable()
            if self._is_host():
                self.delete_btn.enable()
            return
        self._navigate_back()
