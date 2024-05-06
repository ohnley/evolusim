from brain import NeuralBrain
import numpy as np
import pygame


class NeuralBrainVisualizer:
    def __init__(self, _brain: NeuralBrain, screen_width=900, screen_height=700):
        self.brain = _brain
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_layers = len(self.brain.hidden_sizes) + 2
        self.neuron_radius = 12
        self.max_weight = 1.0
        self.neuron_positions = self.gen_positions()
        self.running = False

    def draw(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Neural Brain Visualizer")

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"Mouse clicked at: {event.pos}")
                elif event.type == pygame.VIDEORESIZE:
                    # Resize the screen when the window is resized
                    self.screen_width = event.w
                    self.screen_height = event.h
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.neuron_positions = self.gen_positions()
                    self.draw_connections(screen)
                    self.draw_neurons(screen)
                    pygame.display.flip()  # Update the display

            screen.fill((255, 240, 245))  # Clear the screen with white background
            self.draw_connections(screen)
            self.draw_neurons(screen)

            pygame.display.flip()  # Update the display

        pygame.quit()

    def gen_positions(self):
        positions = []

        # Input Layer
        positions.append(self.gen_layer_positions(self.brain.input_size, 1))
        # Hidden Layers
        for layer in self.brain.hidden_sizes:
            positions.append(self.gen_layer_positions(layer, len(positions) + 1))
        # Output Layer
        positions.append(self.gen_layer_positions(self.brain.output_size, len(positions) + 1))
        return positions

    def gen_layer_positions(self, number_neurons, col_pos):

        # X Coordinate Location
        avail_width = self.screen_width - (self.neuron_radius * 2)
        x_coord = ((avail_width / (self.num_layers + 1)) * col_pos) + self.neuron_radius

        # Y Coordinate Locations
        avail_height = self.screen_height - (self.neuron_radius * 2)
        y_step = (avail_height / (number_neurons + 1))
        y_start = self.neuron_radius
        y_coords = [y_start + (_y * y_step) for _y in range(1, number_neurons+1)]
        return [(x_coord, y_coord) for y_coord in y_coords]

    def draw_neurons(self, screen):
        for layer_positions in self.neuron_positions:
            for position in layer_positions:
                pygame.draw.circle(screen, (0, 200, 190), (int(position[0]), int(position[1])), self.neuron_radius)

    def draw_connections(self, screen):
        for index in range(len(self.neuron_positions)-1):
            start_layer = self.neuron_positions[index]
            end_layer = self.neuron_positions[index+1]
            for start_neuron in start_layer:
                for end_neuron in end_layer:
                    start = (start_neuron[0], start_neuron[1])
                    end = (end_neuron[0], end_neuron[1])
                    pygame.draw.line(screen, (175, 175, 175),
                                     start,
                                     end,
                                     1)


# Example usage
# input_size = 12
# hidden_sizes = [1, 20, 2, 8]
# output_size = 5
#
# brain = NeuralBrain(input_size, hidden_sizes, output_size)
# print(brain)
# visualizer = NeuralBrainVisualizer(brain)
# visualizer.draw()
