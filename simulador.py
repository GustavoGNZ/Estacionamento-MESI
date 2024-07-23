from memory import Memory
from cpu import CPU

class Simulador:
    def __init__(self, num_processors, cache_size, memory_size):
        self.memory = Memory(memory_size) # Memoria Compartilhada
        self.processors = [CPU(i, cache_size) for i in range(num_processors)] # 3 processadores

     