import random

class Memory: # Memoria Ram
    def __init__(self, size):
        self.data = [random.randint(1000, 9999) for _ in range(size)]
        self.size = size

    def read(self, address):
        return self.data[address]

    def write(self, address, data):
        self.data[address] = data
