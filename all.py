from enum import Enum
import random

class Memory:  # Memoria Ram
    def __init__(self, size):
        self.size = size
        self.data = [random.randint(1000, 9999) for _ in range(size)]

    def read(self, endereco):
        return self.data[endereco]
    
    def write(self, endereco, data):
        self.data[endereco] = data

class State(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'

class CacheLine:
    def __init__(self):
        self.endereco = None
        self.data = None
        self.state = State.INVALID

    def update(self, endereco, data, state):
        self.endereco = endereco
        self.data = data
        self.state = state
class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size

    def search(self, endereco):
        for line in self.lines:
            if line.endereco == endereco:
                return line
        return None

    def write(self, endereco, data, state):
        line = self.search(endereco)
        if line:
            line.update(endereco, data, state)
        else:
            line = self.search(None)
            if line:
                line.update(endereco, data, state)
            else:
                line = random.choice(self.lines)
                line.update(endereco, data, state)

    def read(self, endereco, memory):
        line = self.search(endereco)
        if line and line.state != State.INVALID:
            return line.data
        else:
            data = memory.read(endereco)
            self.write(endereco, data, State.SHARED)
            return data

class CacheManager:
    def __init__(self):
        self.caches = {}

    def register_cache(self, processor_id, cache):
        self.caches[processor_id] = cache

    def get_cache(self, processor_id):
        return self.caches.get(processor_id)

    def invalidate_other_caches(self, endereco, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                cache_line = cache.search(endereco)
                if cache_line:
                    cache_line.state = State.INVALID
    
    def read(self, processor_id, endereco, memory):
        cache = self.get_cache(processor_id)
        if cache:
            line = cache.search(endereco)
            if line and line.state != State.INVALID:
                return line.data
        for pid, cache in self.caches.items():
            if pid != processor_id:
                line = cache.search(endereco)
                if line and line.state != State.INVALID:
                    return line.data
        return memory.read(endereco)
    

class Processador:
    def __init__(self, id, cache_size, memory, cache_manager):
        self.id = id
        self.cache = Cache(cache_size)
        self.memory = memory
        self.cache_manager = cache_manager
        cache_manager.register_cache(self.id, self.cache)

    def ler(self, endereco):
        data = self.cache_manager.read(self.id, endereco, self.memory)
        print(f"Processador {self.id} lê o endereço {endereco} com dado {data}")
        return data

    def escrever(self, endereco, valor):
        self.cache_manager.invalidate_other_caches(endereco, self.id)
        self.cache.write(endereco, valor, State.MODIFIED)
        print(f"Processador {self.id} escreve o valor {valor} no endereço {endereco}")


def main():
            memory = Memory(5)
            cache_manager = CacheManager()
            
            processor1 = Processador(1, 4, memory, cache_manager)
            processor2 = Processador(2, 4, memory, cache_manager)
            
            processor1.ler(0)
            processor2.ler(0)
            
            processor1.escrever(0, 999)
            
            processor1.ler(0)
            processor2.ler(0)

            def print_memory_and_caches(memory, cache_manager):
                print("Memory:")
                for i in range(memory.size):
                    print(f"Address {i}: {memory.read(i)}")
                
                print("\nCaches:")
                for processor_id, cache in cache_manager.caches.items():
                    print(f"Processor {processor_id} Cache:")
                    for line in cache.lines:
                        print(f"Address: {line.endereco}, Data: {line.data}, State: {line.state}")

            print_memory_and_caches(memory, cache_manager)

if __name__ == "__main__":
    main()