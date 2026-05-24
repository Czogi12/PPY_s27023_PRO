import argparse
import pygame

from .app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    args = parser.parse_args()

    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    app = App(screen, server_url=args.server)

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
