import pygame
import block
from cell import Cell


class Renderer:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    BLUE = (50, 50, 228)
    GREEN = (50, 255, 228)
    DARK_PINK = (199, 21, 133)

    def __init__(self, arena, cell_size):
        self.arena = arena
        self.cell_size = cell_size

    def draw(self, screen):
        for y in range(self.arena.height):
            for x in range(self.arena.width):
                cell = self.arena.board[y][x]
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, Renderer.WHITE, rect, 1)
                if isinstance(cell, block.Empty):
                    pass
                elif isinstance(cell, Cell):
                    # Draw cell contents based on its type
                    # Customize this part based on your specific cell types and desired visualization
                    pygame.draw.rect(screen, Renderer.DARK_PINK, rect)
                    screen.blit(pygame.font.Font(None, 25).render(str(cell), True,
                                                                  Renderer.WHITE),
                                (x * self.cell_size + (self.cell_size/4),
                                 y * self.cell_size + (self.cell_size/4)))
                elif isinstance(cell, block.Food):
                    pygame.draw.rect(screen, Renderer.GREEN, rect)
                    screen.blit(pygame.font.Font(None, 25).render(str(cell), True,
                                                                  Renderer.BLACK),
                                (x * self.cell_size + (self.cell_size/4),
                                 y * self.cell_size + (self.cell_size/4)))

    def draw_button(self, screen, button_rect, text):
        pygame.draw.rect(screen, Renderer.WHITE, button_rect)
        font = pygame.font.Font(None, 30)
        text_surface = font.render(text, True, Renderer.BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)