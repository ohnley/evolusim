import copy
import block
from config import *
from cell import Cell
from utils import *


class Arena:

    def __init__(self, height=10, width=10, cells=None):
        self.height = height
        self.width = width
        self.board = [[block.Empty() for x in range(self.width)] for y in range(self.height)]
        self.cells = set()
        self.epoch = 0
        self.generation = 0
        self.murders = 0
        self.moves = 0
        self.df = None
        if cells is None:
            pass
        else:
            for cell in cells:
                self.add_cell(cell)

    def __str__(self):
        result: str = ''
        for col in range(self.height):
            for row in range(self.width):
                item = self.board[col][row]
                result += (str(item) + ' | ')
            result += '\n'
        return result

    def is_inbounds(self, x, y):
        return (x >= 0) and (x < self.width) and (y >= 0) and (y < self.height)

    def set_loc(self, x, y, value):
        # print(x, y, value)
        self.board[y][x] = value

    def clear_loc(self, x, y):
        self.board[y][x] = block.Empty()

    def clear_board(self):
        self.board = [[block.Empty() for x in range(self.width)] for y in range(self.height)]
        self.cells.clear()

    def get_loc(self, x, y):
        return self.board[y][x]

    def remove_cell(self, cell_to_remove: Cell):
        self.cells.remove(cell_to_remove)
        self.clear_loc(cell_to_remove.x, cell_to_remove.y)

    def add_cell(self, cell_to_add: Cell):
        self.cells.add(cell_to_add)
        self.set_loc(cell_to_add.x, cell_to_add.y, cell_to_add)

    def update(self):

        action_list = self.get_action_list()
        random.shuffle(action_list)
        self.execute_action_list(action_list)
        self.generation += 1
        # self.df = append_to_dataframe(list_done, self.epoch, self.df)
        self.start_next_gen()

    def start_next_gen(self):
        # We don't need to repopulate if there are enough cells left
        if len(self.cells) > self.height * self.width * REPOP_THRESHOLD:
            return
        else:
            print('gen:', self.generation, ' epoch:', self.epoch, ' murders:', self.murders, ' moves:', self.moves)
            self.murders, self.moves = 0, 0
            self.epoch += 1

        # Determine the number of cells and food spaces to refill
        multiplier = int((self.height * self.width * PERCENT_SPACES_TO_FILL_CELLS) // (len(self.cells)))
        num_new_cells = multiplier * len(self.cells)

        num_new_foods = int((self.height * self.width * PERCENT_SPACES_TO_FILL_FOOD) // 1)
        new_pos = generate_unique_random_points(self.height, self.width, num_new_cells + num_new_foods)

        print(num_new_cells, self.height * self.width * PERCENT_SPACES_TO_FILL_CELLS, multiplier, self.height * self.width * REPOP_THRESHOLD)
        self.repopulate(new_pos[:num_new_cells], multiplier)

        for j in new_pos[num_new_cells:]:
            food = block.Food(random.randint(1, 10))
            self.set_loc(j[0], j[1], food)

    def repopulate(self, positions, multiplier):

        survivors = list(self.cells.copy())
        self.clear_board()
        positions_iter = iter(positions)

        for cell in survivors:
            for _ in range(multiplier):
                x, y = next(positions_iter)
                new_cell = copy.deepcopy(cell)
                new_cell.brain.mutate(MUTATION_PROBABILITY)
                new_cell.update_coords(x, y)
                new_cell.energy = 50
                self.add_cell(new_cell)

    def expend_energy(self, cell: Cell, energy: int):
        if not cell.consume_energy(energy):
            self.remove_cell(cell)

    def eat_food(self, x, y, amount=1):
        target = self.get_loc(x, y)
        if target.get_type() != 'Food':
            raise TypeError(target, "is not food!")
        elif target.energy <= 0:
            self.clear_loc(x, y)
            return False
        elif target.consume(amount):
            return True
        else:
            self.clear_loc(x, y)
            return False

    def get_action_list(self):
        action_list = []
        for cell in self.cells:
            x, y = cell.x, cell.y
            env = {}
            for adjacency in cell.fov:
                if self.is_inbounds(x + adjacency[0], y + adjacency[1]):
                    neighbor = self.get_loc(x + adjacency[0], y + adjacency[1])
                    env[adjacency] = neighbor
                else:
                    env[adjacency] = block.OOB()
            action = cell.get_action(env)
            action_list.append(action)
        return action_list

    #todo: put in cell class
    def execute_action_list(self, action_list):
        for action in action_list:

            # get the action details
            (cell_x, cell_y) = action['loc']
            # cell_y = action['loc'][1]
            action_type = action['type']
            target_x = action['adj'][0] + cell_x
            target_y = action['adj'][1] + cell_y

            cell: Cell = self.get_loc(cell_x, cell_y)
            # execute action if appropriate
            if not self.is_inbounds(target_x, target_y):
                if cell.get_type() == 'Cell':
                    self.expend_energy(cell, OOB_ATTEMPT_COST)

            elif cell.get_type() == 'Cell':

                target = self.get_loc(target_x, target_y)

                if action_type == 'move' and (target.get_type() == 'Empty'):
                    self.remove_cell(cell)
                    cell.update_coords(target_x, target_y)
                    self.add_cell(cell)
                    self.expend_energy(cell, MOVE_COST)
                    self.moves += 1

                elif action_type == 'stab':
                    # self.expend_energy(cell, STAB_COST)
                    # continue
                    if target.get_type() == 'Cell':
                        self.remove_cell(target)
                        cell.energy += target.energy
                        self.murders += 1
                    self.expend_energy(cell, STAB_COST)

                elif action_type == 'eat':
                    if target.get_type() == 'Food':
                        consume_amount = min(1, target.energy)
                        if self.eat_food(target_x, target_y, consume_amount):
                            cell.energy += EAT_SUCCESS_BENEFIT
                    else:
                        self.expend_energy(cell, FAIL_EAT_COST)

                elif action_type == 'reproduce':
                    pass

                else:
                    self.expend_energy(cell, CATCHALL_COST)