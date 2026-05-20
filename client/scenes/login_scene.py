import pygame
import pygame_gui

from client.layouts.column_layout import ColumnLayout
from client.scenes.scene import Scene

class LoginScene(Scene):
    def __init__(self, app, screen):
        super().__init__(app)
        self.ui = pygame_gui.UIManager((screen.width, screen.height))

        width, height = 200, 32
        col = ColumnLayout(
            x=screen.width / 2 - width / 2,
            start_y=screen.height * 0.35,
            width=width,
            height=height,
        )

        self.username = pygame_gui.elements.UITextEntryLine(
            relative_rect=col.next(), manager=self.ui, placeholder_text="Username"
        )
        self.password = pygame_gui.elements.UITextEntryLine(
            relative_rect=col.next(), manager=self.ui, placeholder_text="Password"
        )
        self.password.set_text_hidden(True)
        self.login_btn = pygame_gui.elements.UIButton(
            relative_rect=col.next(), manager=self.ui, text="Log in"
        )
        self.register_btn = pygame_gui.elements.UIButton(
            relative_rect=col.next(), manager=self.ui, text="Register"
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        self.ui.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.login_btn:
                self.__login()
            elif event.ui_element == self.register_btn:
                self.__register()

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self.ui.draw_ui(screen)

    def __login(self) -> None:
        username = self.username.get_text()
        password = self.password.get_text()
        # TODO: POST to /login, then app.change_scene(LobbyBrowserScene(...))
        print(f"login: {username!r}")
        print(username)

    def __register(self) -> None:
        username = self.username.get_text()
        password = self.password.get_text()
        # TODO: POST to /register
        print(f"register: {username!r}")
