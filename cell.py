import random

import numpy as np

from brain import NeuralBrain
from block import Block

FOV = {
    'UDLR': [(0, -1), (0, 1), (-1, 0), (1, 0)],
    '3x3': [(1, 1), (1,0), (1,-1), (0, 1), (0,-1), (-1, 1), (-1, 0), (-1, -1)],
    '5x5': [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, -1),
            (-1, 0), (-1, 1), (-1, 2), (0, -2), (0, -1), (0, 1), (0, 2), (1, -2),
            (1, -1), (1, 0), (1, 1), (1, 2), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]

}
actions = ['stab', 'move', 'mutate', 'reproduce', 'eat']


class Cell(Block):
    def __init__(self, x, y, value, brain=None, fov_type='5x5'):
        self.x = x
        self.y = y
        self.value = value
        self.fov_type = fov_type
        self.fov = FOV[fov_type]
        self.energy = 30

        if brain is None:
            self.brain = NeuralBrain(input_size=len(self.fov)*3, output_size=12)
        else:
            self.brain = brain

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.value})"

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.x == other.x and self.y == other.y
        return False

    def __str__(self):
        return self.value

    def update_coords(self, x, y):
        self.x = x
        self.y = y

    def get_type(self):
        return 'Cell'

    def mutate(self):
        pass

    def consume_energy(self, amount=1):
        if amount < self.energy:
            self.energy -= amount
            return True
        else:
            return False

    def gen_activations(self, inputs):
        return self.brain.forward(inputs)

    def get_action(self, env):
        parsed_inputs = self.process_env(env)
        outputs = self.gen_activations(parsed_inputs)
        action = self.process_activations(outputs)
        return action

    def process_env(self, env):
        parsed_inputs = []
        for adj, cell in env.items():
            if cell.get_type() == 'OOB':
                parsed_inputs += [0, 0, 0]
            elif cell.get_type() == 'Cell':
                parsed_inputs += [1, 0, 0]
            elif cell.get_type() == 'Food':
                parsed_inputs += [0, 1, 0]
            elif cell.get_type() == 'Empty':
                parsed_inputs += [0, 0, 1]
        # print(self.value, self.x, self.y, parsed_inputs)
        return parsed_inputs

    def process_activations(self, activations):

        neuron = np.argmax(activations)
        # print(activations, neuron)
        location = neuron // 3
        option = neuron % 3
        str_act = ''
        if location == 0:
            adj = (-1, 0)
            str_act+='up '
        elif location == 1:
            adj = (1, 0)
            str_act+='down '
        elif location == 2:
            adj = (0, -1)
            str_act+='left '
        elif location == 3:
            adj = (0, 1)
            str_act+='right '

        if option == 0:
            act = 'stab'
            str_act += act
        elif option == 1:
            act = 'eat'
            str_act += act
        else:
            act = 'move'
            str_act += act

        res = {
            'loc': (self.x, self.y),
            'adj': adj,
            'type': act
        }

        # formatted_list = [format(num, '.4f') for num in activations]
        # print('active:', *formatted_list, '  neuron:  ', neuron,    str_act)
        # if random.randint(1,10) > 8:
        #     print('name', self.value, 'location:', location, '  option:', option, 'res: ', res)
        return res
