import numpy as np
import pygame

class Boundry:

    def __init__(self, x1, y1, x2, y2) -> None:
        self.a = (x1, y1)
        self.b = (x2, y2)

    def show(screen):
        pygame.draw.line(screen, (0,0,0), a, b)
          
