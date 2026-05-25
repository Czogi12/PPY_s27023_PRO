import pygame
import pygame_gui

from .logged_scene import LoggedScene


_POLL_INTERVAL = 2.0
_ROW_HEIGHT = 40
_ROW_GAP = 6


class BrowserScene(LoggedScene):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        self._poll_timer = 0.0
        self._lobbies: list[dict] = []
        self._row_buttons: dict[pygame_gui.elements.UIButton, int] = {}

        screen_w = screen.get_width()
        screen_h = screen.get_height()
        content_top = 60
        margin = 20
        create_w = 200
        create_h = 40

        self.create_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (screen_w - create_w) // 2,
                content_top,
                create_w,
                create_h,
            ),
            manager=self.ui,
            text="Create lobby",
        )

        list_top = content_top + create_h + margin
        list_w = min(600, screen_w - 2 * margin)
        list_h = screen_h - list_top - margin
        self.scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(
                (screen_w - list_w) // 2,
                list_top,
                list_w,
                list_h,
            ),
            manager=self.ui,
        )

    def on_enter(self) -> None:
        super().on_enter()
        self._refresh()

    def handle_content_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.create_btn:
            from .create_lobby_scene import CreateLobbyScene
            self.app.change_scene(CreateLobbyScene)
            return
        lobby_id = self._row_buttons.get(event.ui_element)
        if lobby_id is not None:
            self.create_btn.disable()
            for btn in self._row_buttons:
                btn.disable()
            self.app.submit(
                self.app.join_lobby, lobby_id,
                on_done=lambda r, lid=lobby_id: self._on_joined(r, lid),
            )

    def _on_joined(self, result, lobby_id: int) -> None:
        if not self._alive:
            return
        _, error = result
        if error is not None:
            print(f"join failed: {error}")
            self.create_btn.enable()
            for btn in self._row_buttons:
                btn.enable()
            return
        from .lobby_scene import LobbyScene
        self.app.change_scene(LobbyScene, lobby_id=lobby_id)

    def update_content(self, dt: float) -> None:
        self._poll_timer += dt
        if self._poll_timer >= _POLL_INTERVAL:
            self._poll_timer = 0.0
            self._refresh()

    def draw_content(self, surface: pygame.Surface) -> None:
        pass

    def _refresh(self) -> None:
        if not self._alive:
            return
        self.app.submit(self.app.fetch_lobbies, on_done=self._on_lobbies)

    def _on_lobbies(self, result) -> None:
        if not self._alive:
            return
        lobbies, _ = result
        if lobbies is None:
            return
        if self._signature(lobbies) == self._signature(self._lobbies):
            return
        self._lobbies = lobbies
        self._rebuild_rows()

    def _rebuild_rows(self) -> None:
        for btn in list(self._row_buttons):
            btn.kill()
        self._row_buttons.clear()

        inner_w = self.scroll.get_container().get_size()[0]
        for i, lobby in enumerate(self._lobbies):
            label = f"{lobby['name']} {lobby['user_count']}/20"
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    0,
                    i * (_ROW_HEIGHT + _ROW_GAP),
                    inner_w,
                    _ROW_HEIGHT,
                ),
                manager=self.ui,
                container=self.scroll,
                text=label,
            )
            self._row_buttons[btn] = lobby["id"]

        total_h = max(
            1,
            len(self._lobbies) * (_ROW_HEIGHT + _ROW_GAP) - _ROW_GAP,
        )
        self.scroll.set_scrollable_area_dimensions((inner_w, total_h))

    @staticmethod
    def _signature(lobbies: list[dict]) -> list[tuple]:
        return [(l["id"], l["name"], l["user_count"]) for l in lobbies]
