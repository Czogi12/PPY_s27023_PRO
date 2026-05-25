import pygame
import pygame_gui

from ..layouts.column_layout import ColumnLayout
from .logged_scene import LoggedScene


class CreateLobbyScene(LoggedScene):
    def __init__(self, app, screen):
        super().__init__(app, screen)

        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 100, 32),
            manager=self.ui,
            text="Back",
        )

        width, height = 240, 32
        col = ColumnLayout(
            x=(screen.get_width() - width) // 2,
            start_y=screen.get_height() * 0.35,
            width=width,
            height=height,
        )

        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=col.next(),
            manager=self.ui,
            placeholder_text="Lobby name",
        )
        self.create_btn = pygame_gui.elements.UIButton(
            relative_rect=col.next(),
            manager=self.ui,
            text="Create",
        )
        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=col.next(),
            manager=self.ui,
            text="",
        )

    def handle_content_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.back_btn:
            from .browser_scene import BrowserScene
            self.app.change_scene(BrowserScene)
            return
        if event.ui_element == self.create_btn:
            self.__create()

    def update_content(self, dt: float) -> None:
        pass

    def draw_content(self, surface: pygame.Surface) -> None:
        pass

    def __create(self) -> None:
        if not self._alive:
            return
        name = self.name_input.get_text().strip()
        if not name:
            self.error_label.set_text("Name cannot be empty")
            return
        self.error_label.set_text("")
        self.create_btn.disable()
        self.back_btn.disable()
        self.app.submit(self.app.create_lobby, name, on_done=self._on_created)

    def _on_created(self, result) -> None:
        if not self._alive:
            return
        lobby, error = result
        if lobby is None:
            self.error_label.set_text(error or "Failed to create lobby")
            self.create_btn.enable()
            self.back_btn.enable()
            return
        from .lobby_scene import LobbyScene
        self.app.change_scene(LobbyScene, lobby_id=lobby["id"])
