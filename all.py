from enum import Enum
import random

class Memory:
    def __init__(self, size):
        self.size = size
        self.data = [random.randint(1000, 9999) for _ in range(size)]

    def read(self, endereco):
        return self.data[endereco]
    
    def write(self, endereco, data):
        self.data[endereco] = data

    def print_memory(self):
        print("Memória Principal:")
        for i, value in enumerate(self.data):
            print(f"Endereço {i}: {value}")
        print()

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

    def read(self, endereco, memory, cache_manager, processor_id):
        line = self.search(endereco)
        if line and line.state != State.INVALID:
            if line.state == State.EXCLUSIVE:
                cache_manager.update_state_to_shared(endereco, processor_id)
            return line.data
        else:
            data = memory.read(endereco)
            is_shared = cache_manager.is_shared(endereco, processor_id)
            new_state = State.SHARED if is_shared else State.EXCLUSIVE
            self.write(endereco, data, new_state)
            return data

    def update_state(self, endereco, new_state):
        line = self.search(endereco)
        if line:
            line.state = new_state

    def print_cache(self, processor_id):
        print(f"Cache do Processador {processor_id}:")
        for i, line in enumerate(self.lines):
            estado = line.state.value if line.state else "N/A"
            print(f"Linha {i}: Endereço = {line.endereco}, Dado = {line.data}, Estado = {estado}")
        print()

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
                cache.update_state(endereco, State.INVALID)

    def is_shared(self, endereco, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(endereco)
                if line and line.state in {State.SHARED, State.EXCLUSIVE, State.MODIFIED}:
                    return True
        return False

    def update_state_to_shared(self, endereco, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(endereco)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, endereco, memory):
        cache = self.get_cache(processor_id)
        line = cache.search(endereco)
        if line and line.state != State.INVALID:
            if line.state == State.EXCLUSIVE:
                self.update_state_to_shared(endereco, processor_id)
            return line.data
        else:
            data = cache.read(endereco, memory, self, processor_id)
            return data

    def handle_write(self, processor_id, endereco, data, memory):
        self.invalidate_other_caches(endereco, processor_id)
        cache = self.get_cache(processor_id)
        cache.write(endereco, data, State.MODIFIED)
        memory.write(endereco, data)

class Processador:
    def __init__(self, id, cache_size, memory, cache_manager):
        self.id = id
        self.cache = Cache(cache_size)
        self.memory = memory
        self.cache_manager = cache_manager
        cache_manager.register_cache(self.id, self.cache)

    def ler(self, endereco):
        data = self.cache_manager.handle_read(self.id, endereco, self.memory)
        print(f"Processador {self.id} lê o endereço {endereco} com dado {data}")
        return data

    def escrever(self, endereco, valor):
        self.cache_manager.handle_write(self.id, endereco, valor, self.memory)
        print(f"Processador {self.id} escreve o valor {valor} no endereço {endereco}")

    def print_cache(self):
        self.cache.print_cache(self.id)

# def main():
#     memory = Memory(5)
#     cache_manager = CacheManager()

#     # Inicializa os processadores
#     processor1 = Processador(1, 4, memory, cache_manager)
#     processor2 = Processador(2, 4, memory, cache_manager)
#     processor3 = Processador(3, 4, memory, cache_manager)

#     # Realiza algumas operações de leitura e escrita
#     print("Criando Estado Exclusivo (E):")
#     processor1.ler(3)  # Isso deve colocar a linha na cache de processor1 como EXCLUSIVE
#     processor1.print_cache()

#     print("Processador 2 lê o endereço 30 (Estado deve mudar para SHARED):")
#     processor2.ler(3)  # Isso deve colocar a linha na cache de processor2 como SHARED
#     processor1.print_cache()
#     processor2.print_cache()

#     print("Processador 3 escreve no endereço 30 (Invalida as caches de processor1 e processor2):")
#     processor3.escrever(3, 8888)  # Isso deve invalidar as linhas de cache de processor1 e processor2
#     processor1.print_cache()
#     processor2.print_cache()
#     processor3.print_cache()

#     # Imprime a memória principal e o estado das caches
#     memory.print_memory()
#     processor1.print_cache()
#     processor2.print_cache()
#     processor3.print_cache()

# if __name__ == "__main__":
#     main()
