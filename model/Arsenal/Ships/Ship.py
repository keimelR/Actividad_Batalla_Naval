import pygame

class Ship():
    def __init__(
        self, 
        pos_x,
        pos_y,
        height,
        width,
        length
    ):
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill((131, 131, 128))
        self.angle = 90
        self.length = length
        self.is_on_grid = False
        
    def draw(self, screen: pygame.Surface):
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        rotated_rect = rotated_surface.get_rect(center=self.rect.center)
        screen.blit(rotated_surface, rotated_rect)
        
    def rotate(self, angle = 90):
        self.angle = (self.angle + angle) % 360