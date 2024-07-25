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

    def printLine(self):
        print(f"Endereço = {self.endereco}, Dado = {self.data}, Estado = {self.state}")

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = []

    def search(self, endereco):
        for line in self.lines:
            if line.endereco == endereco:
                return line
        return None

    def write(self, endereco, data, state):
        line = self.search(endereco)
        if line:
            # Write Hit (WH)
            if line.state == State.SHARED:
                line.update(endereco, data, State.MODIFIED)
                return "WH"
            elif line.state == State.EXCLUSIVE or line.state == State.MODIFIED:
                line.update(endereco, data, State.MODIFIED)
                return "WH"
        else:
            # Write Miss (WM)
            line = self.search(None)
            if line:
                empty_lines = [l for l in self.lines if l.endereco is None]
                if empty_lines:
                    line = random.choice(empty_lines)
                    line.update(endereco, data, state)
                    self.fifoQueue.append(self.lines.index(line))
                    return "WM"
            elif self.is_full():
                index = self.fifoQueue.pop(0)
                line_to_remove = self.lines[index]
                endereco_to_remove = line_to_remove.endereco
                data_to_remove = line_to_remove.data
                self.lines[index] = CacheLine()
                self.write(endereco, data, state)
                return "WM"

    def read(self, endereco, memory, cache_manager, processor_id):
        line = self.search(endereco)
        if line and line.state != State.INVALID:
            # Read Hit (RH)
            return line.data, "RH"
        else:
            # Read Miss (RM)
            data = memory.read(endereco)
            is_shared = cache_manager.is_shared(endereco, processor_id)
            new_state = State.SHARED if is_shared else State.EXCLUSIVE
            self.write(endereco, data, new_state)
            return data, "RM"

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

    def is_full(self):
        return len(self.lines) >= self.size

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
        for pid, cache in self.caches.items():
            line = cache.search(endereco)
            if line and line.state != State.INVALID:
                if line.state == State.MODIFIED and pid != processor_id:
                    # Write the modified data to memory
                    memory.write(endereco, line.data)
                    # Update the state to shared
                    self.update_state_to_shared(endereco, processor_id)
                    # Write the data to the requesting processor's cache
                    self.caches[processor_id].write(endereco, line.data, State.SHARED)
                    # Update the responding cache's state to shared
                    line.state = State.SHARED
                    return line.data, "RH"
                if line.state == State.EXCLUSIVE and pid != processor_id:
                    self.update_state_to_shared(endereco, processor_id)
                    self.caches[processor_id].write(endereco, line.data, State.SHARED)
                    return line.data, "RH"
        # If no cache has the data, read from memory
        data, transacao = self.caches[processor_id].read(endereco, memory, self, processor_id)
        return data, transacao

    def handle_write(self, processor_id, endereco, data, memory):
        self.invalidate_other_caches(endereco, processor_id)
        cache = self.get_cache(processor_id)
        transacao = cache.write(endereco, data, State.MODIFIED)
        return transacao

class Processador:
    def __init__(self, id, cache_size, memory, cache_manager):
        self.id = id
        self.cache = Cache(cache_size)
        self.memory = memory
        self.cache_manager = cache_manager
        cache_manager.register_cache(self.id, self.cache)

    def ler(self, endereco):
        data, transacao = self.cache_manager.handle_read(self.id, endereco, self.memory)
        print(f"Processador {self.id} lê o endereço {endereco} com dado {data} ({transacao})\n")
        return data

    def escrever(self, endereco, valor):
        transacao = self.cache_manager.handle_write(self.id, endereco, valor, self.memory)
        print(f"Processador {self.id} escreve o valor {valor} no endereço {endereco} ({transacao})\n")

    def print_cache(self):
        self.cache.print_cache(self.id)


def memoTamanho():
    tamanho = int(input("Digite o tamanho da memória (minimo 50): "))
    if tamanho < 50:
        print("Tamanho inválido, digite novamente")
        memoTamanho()
    return tamanho

def cacheTamanho():
    tamanho = int(input("Digite o tamanho da cache (minimo 5): "))
    if tamanho < 5:
        print("Tamanho inválido, digite novamente")
        cacheTamanho()
    return tamanho


def test_read_write(processors):
    # Teste de leitura e escrita
    
    # Processador 1 lê endereço 0 (Read Miss - RM)
    processors[0].ler(0)
    processors[0].print_cache()

    # Processador 1 lê endereço 0 novamente (Read Hit - RH)
    processors[0].ler(0)
    processors[0].print_cache()

    # Processador 2 lê endereço 0 (Read Miss - RM, mas estado deve mudar para SHARED)
    processors[1].ler(0)
    processors[0].print_cache() 
    processors[1].print_cache()

    # Processador 2 escreve no endereço 2 (Write Miss - WM)
    processors[1].escrever(2, 8765)
    processors[1].print_cache()

    # Processador 3 lê endereço 2 (Read Miss - RM, mas estado deve mudar para SHARED)
    processors[2].ler(2)
    processors[2].print_cache()

    # Processador 1 lê endereço 2 (Read Hit - RH, pois está compartilhado)
    processors[0].ler(2)
    processors[0].print_cache()


def main():

    # tamanho_memoria = memoTamanho()
    # tamanho_cache = cacheTamanho()
    
    memory = Memory(5)
    cache_manager = CacheManager()

    # Inicializa os processadores
    processor1 = Processador(1, 4, memory, cache_manager)
    processor2 = Processador(2, 4, memory, cache_manager)
    processor3 = Processador(3, 4, memory, cache_manager)

    processors = [processor1, processor2, processor3]

    memory.print_memory()

    test_read_write(processors)

    memory.print_memory()

    # Imprime a memória principal e o estado das caches
    # memory.print_memory()
    for p in processors:
        p.print_cache()


if __name__ == "__main__":
    main()
