from abc import abstractmethod

import pygame
import pygame_gui

from .scene import Scene


class LoggedScene(Scene):
    def __init__(self, app, screen):
        super().__init__(app)
        self.screen = screen
        self.ui = pygame_gui.UIManager((screen.get_width(), screen.get_height()))
        self._username_font = pygame.font.Font(None, 24)

        bar_height = 32
        margin = 10
        btn_width = 100

        self.logout_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                screen.get_width() - btn_width - margin,
                margin,
                btn_width,
                bar_height,
            ),
            manager=self.ui,
            text="Log out",
        )

    def on_enter(self) -> None:
        if self.app.user is None and self.app.token is not None:
            self.app.submit(self.app.fetch_me, on_done=self._on_fetched_me)

    def _on_fetched_me(self, result) -> None:
        if not self._alive:
            return
        from ..models.user import User
        data, _ = result
        if data is not None:
            self.app.user = User(password_hash="", **data)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.ui.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.logout_btn:
            self.__logout()
            return
        self.handle_content_event(event)

    def update(self, dt: float) -> None:
        self.ui.update(dt)
        self.update_content(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_content(surface)
        self.ui.draw_ui(surface)
        if self.app.user is not None:
            text = self._username_font.render(self.app.user.name, True, (255, 255, 255))
            surface.blit(text, (10, 10))

    @abstractmethod
    def handle_content_event(self, event: pygame.event.Event) -> None:
        ...

    @abstractmethod
    def update_content(self, dt: float) -> None:
        ...

    @abstractmethod
    def draw_content(self, surface: pygame.Surface) -> None:
        ...

    def __logout(self) -> None:
        from .login_scene import LoginScene

        self.app.token = None
        self.app.user = None
        self.app.change_scene(LoginScene)
