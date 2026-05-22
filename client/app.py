from scenes.login_scene import LoginScene


class App:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.scene = LoginScene(self, screen)
        pass