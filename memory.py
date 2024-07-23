import random

class Memory: # Memoria Ram
    def __init__(self, size):
        self.data = [random.randint(1000, 9999) for _ in range(size)]
        self.size = size

