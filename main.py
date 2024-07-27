from enum import Enum
import random

class State(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'

class CacheLine:
    def __init__(self):
        self.address = None
        self.data = None
        self.state = State.INVALID

    def update(self, address, data, state):
        self.address = address
        self.data = data
        self.state = state

    def print_line(self, line_index):
        state = self.state.value if self.state else "N/A"
        print(f"Linha {line_index}: Endereço = {self.address}, Dado = {self.data}, Estado = {state}")

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = []

    def search(self, address):
        return next((line for line in self.lines if line.address == address), None)

    def write(self, address, data, state):
        line = self.search(address)
        if line:
            return self.update_existing_line(line, address, data)
        return self.add_or_replace_line(address, data, state)

    def update_existing_line(self, line, address, data):
        if line.state in [State.SHARED, State.MODIFIED, State.EXCLUSIVE]:
            line.update(address, data, State.MODIFIED)
            return "WH", None, None

    def add_or_replace_line(self, address, data, state):
        line = self.search(None)
        if line:
            self.add_to_cache(line, address, data, state)
            return "WM", None, None
        if self.is_full():
            return self.replace_line_in_cache(address, data, state)
        return "WM", None, None

    def add_to_cache(self, line, address, data, state):
        line.update(address, data, state)
        self.fifoQueue.append(self.lines.index(line))

    def replace_line_in_cache(self, address, data, state):
        index = self.fifoQueue.pop(0)
        line_to_remove = self.lines[index]
        address_to_remove, data_to_remove = line_to_remove.address, line_to_remove.data
        self.lines[index] = CacheLine()
        self.write(address, data, state)
        return "WM", address_to_remove, data_to_remove

    def read(self, address, memory, cache_manager, processor_id):
        line = self.search(address)
        if line and line.state != State.INVALID:
            return line.data, "RH"
        return self.handle_cache_miss(address, memory, cache_manager, processor_id)

    def handle_cache_miss(self, address, memory, cache_manager, processor_id):
        data = memory.read(address)
        is_shared = cache_manager.is_shared(address, processor_id)
        new_state = State.SHARED if is_shared else State.EXCLUSIVE
        self.write(address, data, new_state)
        return data, "RM"

    def update_state(self, address, new_state):
        line = self.search(address)
        if line:
            line.state = new_state

    def print_cache(self, processor_id):
        print(f"Cache do Processador {processor_id}:")
        for i, line in enumerate(self.lines):
            line.print_line(i)
        print()

    def is_full(self):
        return all(line.address is not None for line in self.lines)

class Memory:
    def __init__(self, size):
        self.size = size
        self.data = [0 for _ in range(size)]

    def read(self, address):
        return self.data[address]
    
    def write(self, address, data):
        self.data[address] = data

    def print_memory(self):
        print("Memória Principal:")
        for i, value in enumerate(self.data):
            print(f"Endereço {i}: {value}")
        print()

class CacheManager:
    def __init__(self, memory):
        self.caches = {}
        self.memory = memory

    def register_cache(self, processor_id, cache):
        self.caches[processor_id] = cache

    def get_cache(self, processor_id):
        return self.caches.get(processor_id)

    def invalidate_other_caches(self, address, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                cache.update_state(address, State.INVALID)

    def is_shared(self, address, excluding_processor_id):
        return any(self.is_line_shared(pid, address) for pid in self.caches if pid != excluding_processor_id)

    def is_line_shared(self, processor_id, address):
        line = self.caches[processor_id].search(address)
        return line and line.state in {State.SHARED, State.EXCLUSIVE, State.MODIFIED}

    def update_state_to_shared(self, address, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, address, memory):
        # Verificar se o dado está presente em qualquer cache
        for pid, cache in self.caches.items():
            line = cache.search(address)
            if line and line.state != State.INVALID:
                # Dado encontrado em outra cache
                print(f"Processador {processor_id} lê o endereço {address} com dado {line.data} ({'RH'})")
                return line.data, 'RH'

        # Cache Miss: Read from memory and update all caches
        data = memory.read(address)
        is_shared = self.is_shared(address, processor_id)

        # Atualizar todos os caches com o novo estado
        new_state = State.SHARED if is_shared else State.EXCLUSIVE
        for cache in self.caches.values():
            cache.write(address, data, new_state)
        self.update_state_to_shared(address, processor_id)

        print(f"Processador {processor_id} lê o endereço {address} com dado {data} ({'RM'})")
        return data, 'RM'

    def is_line_modified_or_exclusive(self, processor_id, address):
        return any(self.check_and_handle_modified_exclusive(pid, processor_id, address) for pid in self.caches if pid != processor_id)

    def check_and_handle_modified_exclusive(self, current_pid, request_pid, address):
        line = self.caches[current_pid].search(address)
        if line and line.state in {State.MODIFIED, State.EXCLUSIVE}:
            self.handle_state_update(current_pid, request_pid, address, line)
            return True
        return False

    def handle_state_update(self, request_pid, address, line):
        if self.caches[request_pid].is_full():
            self.memory.write(address, line.data)
        self.update_state_to_shared(address, request_pid)
        self.caches[request_pid].write(address, line.data, State.SHARED)
        line.state = State.SHARED

    def handle_write(self, processor_id, address, data, memory):
        self.invalidate_other_caches(address, processor_id)
        cache = self.get_cache(processor_id)
        transaction, old_address, old_data = cache.write(address, data, State.MODIFIED)
        if data == 0:
            memory.write(address, data)
        if transaction == 'WM' and old_address is not None and old_data is not None:
            memory.write(old_address, old_data)
        return transaction


class Processor:
    def __init__(self, id, cache_size, memory, cache_manager):
        """
        Inicializa um objeto Processor.

        Args:
            id (int): O identificador do processador.
            cache_size (int): O tamanho da cache do processador.
            memory (Memory): O objeto Memory que representa a memória principal.
            cache_manager (CacheManager): O objeto CacheManager responsável por gerenciar as caches.

        """
        self.id = id
        self.cache = Cache(cache_size)
        self.memory = memory
        self.cache_manager = cache_manager
        cache_manager.register_cache(self.id, self.cache)

    def read(self, address):
        """
        Realiza uma leitura de dado na memória.

        Args:
            address (int): O endereço de memória a ser lido.

        Returns:
            O dado lido da memória.

        """
        data, transaction = self.cache_manager.handle_read(self.id, address, self.memory)
        print(f"Processador {self.id} lê o endereço {address} com dado {data} ({transaction})\n")
        return data

    def write(self, address, value):
        """
        Realiza uma escrita de dado na memória.

        Args:
            address (int): O endereço de memória a ser escrito.
            value: O valor a ser escrito na memória.

        """
        transaction = self.cache_manager.handle_write(self.id, address, value, self.memory)
        print(f"Processador {self.id} escreve o valor {value} no endereço {address} ({transaction})\n")

    def print_cache(self):
        """
        Imprime o conteúdo da cache do processador.

        """
        self.cache.print_cache(self.id)

class Car:
    def __init__(self, id):
        self.id = id
        self.processor_id = None

class ParkingSlot:
    def __init__(self, id):
        self.id = id
        self.occupied_by = None
    
    def is_occupied(self):
        return self.occupied_by is not None

    def is_occupied_by(self, car_id):
        return self.occupied_by and self.occupied_by.id == car_id

class ParkingLot:
    def __init__(self, size):
        self.slots = [ParkingSlot(i) for i in range(size)]

    def print_slots(self):
        print("Estado das Vagas:")
        for slot in self.slots:
            status = f"Ocupada por Carro {slot.occupied_by.id}" if slot.occupied_by else "Vaga Livre"
            print(f"Vaga {slot.id}: {status}")

    def is_car_parked(self, car_id):
        for slot in self.slots:
            if slot.occupied_by and slot.occupied_by.id == car_id:
                return True
        return False
    
    def is_slot_free(self, slot_id):
        return not self.slots[slot_id].is_occupied()
    
    def is_slot_occupied_by_car(self, slot_id, car_id):
        return self.slots[slot_id].is_occupied_by(car_id)

class ParkingManager:
    def __init__(self, parking_lot, cache_manager):
        self.parking_lot = parking_lot
        self.cache_manager = cache_manager

    def park_car(self, processor_id, car_id, slot_id):
        if self.parking_lot.is_slot_occupied_by_car(slot_id, car_id):
            return self.print_error(f"Erro: Carro {car_id} já está estacionado em outra vaga")

        if not self.parking_lot.is_slot_free(slot_id):
            return self.print_error(f"Erro: Vaga {slot_id} já está ocupada")

        self.perform_park_car(processor_id, car_id, slot_id)

    def perform_park_car(self, processor_id, car_id, slot_id):
        car = Car(car_id)
        car.processor_id = processor_id
        slot_address = slot_id
        transaction = self.cache_manager.handle_write(processor_id, slot_address, car.id, self.cache_manager.memory)

        self.log_transaction(transaction, car_id, slot_id, processor_id)
        self.parking_lot.slots[slot_id].occupied_by = car

    def remove_car(self, processor_id, slot_id):
        slot = self.parking_lot.slots[slot_id]
        if slot.is_occupied():
            if slot.occupied_by.processor_id == processor_id:
                self.perform_remove_car(processor_id, slot_id)
            else:
                return self.print_error(f"Erro: Somente o Processador {slot.occupied_by.processor_id} pode remover o Carro {slot.occupied_by.id}")
        else:
            return self.print_error(f"Erro: Vaga {slot_id} já está livre")
        
    def perform_remove_car(self, processor_id, slot_id):
        self.cache_manager.handle_write(processor_id, slot_id, 0, self.cache_manager.memory)
        self.parking_lot.slots[slot_id].occupied_by = None

    def check_slot(self, processor_id, slot_id):
        car_id, transaction = self.cache_manager.handle_read(processor_id, slot_id, self.cache_manager.memory)
        status = f"Ocupada por Carro {car_id}" if car_id != 0 else "Livre"
        print(f"Vaga {slot_id} está {status}")

    def move_car(self, processor_id, from_slot_id, to_slot_id):
        car = self.parking_lot.slots[from_slot_id].occupied_by
        if not car:
            return self.print_error(f"Erro: Vaga {from_slot_id} está livre")
        if self.parking_lot.slots[to_slot_id].occupied_by:
            return self.print_error(f"Erro: Vaga {to_slot_id} já está ocupada")

        self.remove_car(processor_id, from_slot_id)
        self.park_car(processor_id, car.id, to_slot_id)

    def log_transaction(self, transaction, car_id, slot_id, processor_id):
        if transaction == 'WH':
            print(f"Carro {car_id} estacionado na Vaga {slot_id} pelo Processador {processor_id} - WH")
        elif transaction == 'WM':
            print(f"Carro {car_id} estacionado na Vaga {slot_id} pelo Processador {processor_id} - WM")

    def print_error(self, message):
        print(message)

def get_size(prompt, min_size):
    tamanho = int(input(f"{prompt} (minimo {min_size}): "))
    if tamanho < min_size:
        print("Tamanho inválido, digite novamente")
        return get_size(prompt, min_size)
    return tamanho

def get_memory_size():
    return get_size("Digite o tamanho da memória", 50)

def get_cache_size():
    return get_size("Digite o tamanho da cache", 5)

def test():
    tamanho_memoria = get_memory_size()
    tamanho_cache = get_cache_size()
    
    memory = Memory(tamanho_memoria)
    cache_manager = CacheManager(memory)

    # Inicializa os processadores
    processor1 = Processor(1, tamanho_cache, memory, cache_manager)
    processor2 = Processor(2, tamanho_cache, memory, cache_manager)
    processor3 = Processor(3, tamanho_cache, memory, cache_manager)

    processors = [processor1, processor2, processor3]

    parking_lot = ParkingLot(10)  # Tamanho do estacionamento
    parking_manager = ParkingManager(parking_lot, cache_manager)

    print("Estado inicial do estacionamento:")
    parking_lot.print_slots()

    # Estacionar carros
    print("\nEstacionando carros:")
    parking_manager.park_car(1, 101, 1)
    parking_manager.park_car(2, 102, 2)
    parking_manager.park_car(1, 103, 3)
    parking_manager.park_car(1, 104, 4)
    processor1.print_cache()
    memory.print_memory()
    
    #Tentar mover um carro (opcional)
    parking_manager.move_car(1, 1, 9)
    parking_manager.check_slot(1, 1)
    parking_manager.check_slot(2, 41)

    # Estacionar mais um carro
    parking_manager.park_car(1, 105, 5)

    # Remover um carro
    parking_manager.remove_car(1, 1)

    # Estacionar um carro com outro processador
    parking_manager.park_car(2, 222, 1)

    # Imprimir o estado final das caches e da memória principal
    for p in processors:
        p.print_cache()

    # memory.print_memory()
    parking_lot.print_slots()

def main():
    test()

if __name__ == "__main__":
    main()

