from abc import ABC, abstractmethod


class Block(ABC):

    @abstractmethod
    def get_type(self):
        pass


# Also create some basic subclasses. We will break these out later if they become more complex
class Empty(Block):

    def __str__(self):
        return '.'
    def get_type(self):
        return "Empty"


class OOB(Block):
    def get_type(self):
        return "OOB"

class Food(Block):

    def __init__(self, value):
        self.energy = value

    def __str__(self):
        return str(self.energy)

    def consume(self, amount=1):
        if self.energy >= amount:
            self.energy -= amount
            return True
        else:
            return False

    def get_type(self):
        return "Food"



