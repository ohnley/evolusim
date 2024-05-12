import copy
import random
import block
from cell import Cell
import pandas as pd


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
        self.board[y][x] = value

    def clear_loc(self, x, y):
        self.board[y][x] = block.Empty()

    def get_loc(self, x, y) :
        return self.board[y][x]

    def remove_cell(self, cell_to_remove: Cell):
        self.cells.remove(cell_to_remove)
        self.board[cell_to_remove.y][cell_to_remove.x] = block.Empty()

    def add_cell(self, cell_to_add: Cell):
        self.cells.add(cell_to_add)
        self.board[cell_to_add.y][cell_to_add.x] = cell_to_add

    def update(self):
        action_list = self.get_action_list()
        random.shuffle(action_list)
        list_done = self.execute_action_list(action_list)
        self.df = self.append_to_dataframe(list_done, self.epoch, self.df)
        if len(self.cells) <= (self.height * self.width)/10:
            self.repopulate()
            self.generation += 1
            print('gen:', self.generation, ' epoch:', self.epoch, ' murders:', self.murders, ' moves:', self.moves)
            self.murders = 0
            self.moves = 0

        self.epoch += 1

    def append_to_dataframe(self, actions_taken, epoch, df=None):
        # Define a mapping from tuples to directions
        direction_mapping = {
            (0, 1):  'down',
            (0, -1): 'up',
            (1, 0):  'right',
            (-1, 0): 'left'
        }

        # Flatten the dictionary
        flattened_data = {}
        for action, directions in actions_taken.items():
            for direction, value in directions.items():
                flattened_data[f"{action}_{direction_mapping[direction]}"] = value

        # Add the epoch variable to the flattened data
        flattened_data['epoch'] = epoch

        # Create a DataFrame from the flattened data
        new_df = pd.DataFrame([flattened_data])

        # Append the new DataFrame to the existing DataFrame (if provided)
        if df is None:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

        return df

    def repopulate(self, multiplier=5):

        new_cells = set()

        # todo: move to utls
        def generate_unique_random_points(height, width, n):
            if n > height * width:
                raise ValueError(f"Cannot generate {n} unique points in a {height}x{width} grid.")

            all_points = [(x, y) for x in range(width) for y in range(height)]
            random.shuffle(all_points)
            return all_points[:n]

        new_pos = generate_unique_random_points(self.height, self.width, (len(self.cells)*multiplier) + 10)
        i = 0

        #todo: simplify this
        for cell in list(copy.deepcopy(self.cells)):
            self.remove_cell(cell)
            for _ in range(multiplier):
                new_cell = copy.deepcopy(cell)
                new_cell.brain.mutate(.1)
                new_cell.update_coords(new_pos[i][0], new_pos[i][1])
                new_cell.energy = 50
                i += 1
                new_cells.add(new_cell)

        for cell in new_cells:
            self.add_cell(cell)

        # todo: add to settings
        for j in range(1, 5):
            food = block.Food(random.randint(1, 10))
            self.set_loc(new_pos[-j][0], new_pos[-j][1], food)

    def expend_energy(self, cell: Cell, energy: int):
        if cell.consume_energy(energy):
            pass
        else:
            self.remove_cell(cell)

    def eat_food(self, x, y, amount=1):
        target: block.Block = self.get_loc(x, y)
        if target.get_type() != 'Food':
            raise TypeError(target, "is not food!")
        elif target.energy <= 0:
                self.clear_loc(x, y)
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

            # returns (cell_loc, adjacency, action)
            action = cell.get_action(env)
            action_list.append(action)
        return action_list

    #todo: put in cell class
    def execute_action_list(self, action_list):
        actions_taken = {
            'move': {
                (0,  1): 0,
                (0, -1): 0,
                (1,  0): 0,
                (-1, 0): 0,
            },
            'stab': {
                (0, 1):  0,
                (0, -1): 0,
                (1, 0):  0,
                (-1, 0): 0,
            },
            'eat': {
                (0, 1):  0,
                (0, -1): 0,
                (1, 0):  0,
                (-1, 0): 0,
            }
        }
        for action in action_list:

            # get the action details
            cell_x = action['loc'][0]
            cell_y = action['loc'][1]
            action_type = action['type']
            target_x = action['adj'][0] + cell_x
            target_y = action['adj'][1] + cell_y

            actions_taken[action_type][action['adj']] += 1

            cell: Cell = self.get_loc(cell_x, cell_y)
            # execute action if appropriate
            if not self.is_inbounds(target_x, target_y):
                if cell.get_type() == 'Cell':
                    self.expend_energy(cell, 5)

            elif cell.get_type() == 'Cell':

                target = self.get_loc(target_x, target_y)

                if action_type == 'move' and (target.get_type() == 'Empty'):
                    self.remove_cell(cell)
                    cell.update_coords(target_x, target_y)
                    self.add_cell(cell)
                    self.expend_energy(cell, 1)
                    self.moves += 1

                elif action_type == 'stab':
                    if target.get_type() == 'Cell':
                        self.remove_cell(target)
                        cell.energy += target.energy
                        self.murders += 1
                    self.expend_energy(cell, 1)

                elif action_type == 'eat':
                    if target.get_type() == 'Food':
                        consume_amount = min(1, target.energy)
                        if self.eat_food(target_x, target_y, consume_amount):
                            cell.energy += 5
                    else:
                        self.expend_energy(cell, 5)


                elif action_type == 'reproduce':
                    pass

                else:
                    self.expend_energy(cell, 2)


        return actions_taken
