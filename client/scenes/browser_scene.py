import pygame

from .logged_scene import LoggedScene


class BrowserScene(LoggedScene):
    def handle_content_event(self, event: pygame.event.Event) -> None:
        pass

    def update_content(self, dt: float) -> None:
        pass

    def draw_content(self, surface: pygame.Surface) -> None:
        pass
