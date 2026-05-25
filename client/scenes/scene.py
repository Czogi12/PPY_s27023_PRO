from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from client.app import App


class Scene(ABC):
    def __init__(self, app):
        self.app: App = app
        self._alive: bool = True

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
        self._alive = False
        ui = getattr(self, "ui", None)
        if ui is not None:
            ui.clear_and_reset()
