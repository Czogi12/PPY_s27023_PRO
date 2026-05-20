from abc import ABC, abstractmethod
import pygame

class Scene(ABC):
    def __init__(self, app):
        self.app = app

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        ...

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass