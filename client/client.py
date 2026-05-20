import pygame

from client.app import App


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    app = App(screen)

    pygame.display.set_caption("Game!")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            app.scene.handle_event(event)
        dela = clock.tick(60) / 1e3
        app.scene.update(dela)
        app.scene.draw(screen)
        pygame.display.update()

    pygame.quit()