import pygame

class ColumnLayout:
    def __init__(self, x, start_y, width, height, gap=10):
        self.x, self.y, self.w, self.h, self.gap = x, start_y, width, height, gap

    def next(self) -> pygame.Rect:
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.y += self.h + self.gap
        return rect