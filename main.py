from arena import Arena
from renderer import Renderer
import pygame
from block import Food
from cell import Cell
from neuralbrainvisualizer import NeuralBrainVisualizer
from string import ascii_lowercase as alc
import random



# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)


def create_arena(x, y, cell_ratio=3, food_ratio=5):

    cells = x*y//cell_ratio
    food = x*y//food_ratio

    def alphabet_string(n):
        if n <= 26:
            return chr(ord('A') + n - 1)
        else:
            quotient, remainder = divmod(n - 1, 26)
            return alphabet_string(quotient) + chr(ord('A') + remainder)

    def generate_unique_random_points(height, width, n):
        total_possible_points = height * width
        if n > total_possible_points:
            raise ValueError(f"Cannot generate {n} unique points in a {height}x{width} grid.")

        all_points = [(x, y) for x in range(width) for y in range(height)]
        random.shuffle(all_points)
        return all_points[:n]

    points = generate_unique_random_points(x, y, cells+food)
    cell_set = set()

    for i in range(cells):
        cell = Cell(points[i][0], points[i][1], alphabet_string(i))
        cell_set.add(cell)

    arena_new = Arena(x, y, cell_set)

    for j in range(food):
        food = Food(random.randint(1, 10))
        arena_new.set_loc(points[j+cells][0], points[j+cells][1], food)
    return arena_new


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    arena = create_arena(20, 20)

    pygame.init()

    cell_size = 40
    renderer = Renderer(arena, cell_size)
    screen = pygame.display.set_mode((arena.width * cell_size, arena.height * cell_size + 100))
    clock = pygame.time.Clock()

    update_button = pygame.Rect(0, arena.height * cell_size, arena.width * cell_size // 2, 50)
    auto_progress_button = pygame.Rect(arena.width * cell_size // 2, arena.height * cell_size, arena.width * cell_size // 2, 50)

    auto_progress = False
    update_event = pygame.USEREVENT + 1
    pygame.time.set_timer(update_event, 20)  # Update every 20 milliseconds

    visualizers = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if update_button.collidepoint(event.pos):
                    arena.update()
                elif auto_progress_button.collidepoint(event.pos):
                    auto_progress = not auto_progress
                else:
                    x, y = event.pos
                    if x < arena.width * cell_size and y < arena.height * cell_size:
                        # Calculate the clicked cell coordinates
                        cell_x = x // cell_size
                        cell_y = y // cell_size

                        # Get the clicked cell
                        cell = arena.board[cell_y][cell_x]
                        if cell.get_type() == 'Cell':
                            # Create a new window with the NeuralBrainVisualizer
                            neural_brain_visualizer = NeuralBrainVisualizer(cell.brain)
                            visualizers.append(neural_brain_visualizer)

            elif event.type == update_event and auto_progress:
                arena.update()

        screen.fill(BLACK)
        renderer.draw(screen)
        renderer.draw_button(screen, update_button, "Update")
        renderer.draw_button(screen, auto_progress_button, "Auto Progress: " + ("On" if auto_progress else "Off"))
        pygame.display.flip()
        clock.tick(30)

        # Update neural brain visualizers
        for visualizer in visualizers:
            visualizer.draw()

    arena.df.to_csv("actions_take.csv")
    pygame.quit()