import random
from memory import Memory
class CacheLine:
    def __init__(self):
        self.tag = None
        self.data = None
        self.state = 'I'  # Estados: M (modificado), E (exclusivo), S (compartilhado), I (inválido)

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
