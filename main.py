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

    def print_line(self):
        print(f"Endereço = {self.address}, Dado = {self.data}, Estado = {self.state}")

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = []

    def search(self, address):
        for line in self.lines:
            if line.address == address:
                return line
        return None

    def write(self, address, data, state):
        line = self.search(address)
        if line:
            if line.state in [State.SHARED, State.MODIFIED, State.EXCLUSIVE]:
                line.update(address, data, State.MODIFIED)
                return "WH", None, None
        else:
            line = self.search(None)
            if line:
                empty_lines = [l for l in self.lines if l.address is None]
                if empty_lines:
                    line = random.choice(empty_lines)
                    line.update(address, data, state)
                    self.fifoQueue.append(self.lines.index(line))
                    return "WM", None, None
            elif self.is_full():
                index = self.fifoQueue.pop(0)
                line_to_remove = self.lines[index]
                address_to_remove = line_to_remove.address
                data_to_remove = line_to_remove.data
                self.lines[index] = CacheLine()
                self.write(address, data, state)
                return "WM", address_to_remove, data_to_remove
        return "WM", None, None

    def read(self, address, memory, cache_manager, processor_id):
        line = self.search(address)
        if line and line.state != State.INVALID:
            return line.data, "RH"
        else:
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
            state = line.state.value if line.state else "N/A"
            print(f"Linha {i}: Endereço = {line.address}, Dado = {line.data}, Estado = {state}")
        print()

    def is_full(self):
        for line in self.lines:
            if line.address is None:
                return False
        return True
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
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state in {State.SHARED, State.EXCLUSIVE, State.MODIFIED}:
                    return True
        return False

    def update_state_to_shared(self, address, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, address, memory):
        for pid, cache in self.caches.items():
            line = cache.search(address)
            if line and line.state != State.INVALID:
                if line.state == State.MODIFIED and pid != processor_id:
                    if self.caches[processor_id].is_full():
                        memory.write(address, line.data)
                    self.update_state_to_shared(address, processor_id)
                    self.caches[processor_id].write(address, line.data, State.SHARED)
                    line.state = State.SHARED
                    return line.data, "RH"
                if line.state == State.EXCLUSIVE and pid != processor_id:
                    if self.caches[processor_id].is_full():
                        memory.write(address, line.data)
                    self.update_state_to_shared(address, processor_id)
                    self.caches[processor_id].write(address, line.data, State.SHARED)
                    return line.data, "RH"
        data, transaction = self.caches[processor_id].read(address, memory, self, processor_id)
        return data, transaction

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

class Car:
    def __init__(self, id):
        self.id = id
        self.processor_id = None

class ParkingSlot:
    def __init__(self, id):
        self.id = id
        self.occupied_by = None

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

class ParkingManager:
    def __init__(self, parking_lot, cache_manager):
        self.parking_lot = parking_lot
        self.cache_manager = cache_manager

    def park_car(self, processor_id, car_id, slot_id):
        car = Car(car_id)
        car.processor_id = processor_id

        if self.parking_lot.is_car_parked(car_id):
            print(f"Erro: Carro {car_id} já está estacionado em outra vaga")
            return

        slot = self.parking_lot.slots[slot_id]

        if slot.occupied_by:
            print(f"Erro: Vaga {slot_id} já está ocupada por Carro {slot.occupied_by.id}")
            return

        slot_address = slot_id
        transaction = self.cache_manager.handle_write(processor_id, slot_address, car.id, self.cache_manager.memory)
        
        if transaction == "WH":
            print(f"Write Hit: Carro {car_id} estacionado na Vaga {slot_id} pelo Processador {processor_id}")
        elif transaction == "WM":
            print(f"Write Miss: Carro {car_id} estacionado na Vaga {slot_id} pelo Processador {processor_id}")

        slot.occupied_by = car

    def remove_car(self, processor_id, slot_id):
        slot = self.parking_lot.slots[slot_id]

        if not slot.occupied_by:
            print(f"Erro: Vaga {slot_id} já está livre")
            return

        if slot.occupied_by.processor_id != processor_id:
            print(f"Erro: Somente o Processador {slot.occupied_by.processor_id} pode remover o Carro {slot.occupied_by.id}")
            return

        slot_address = slot_id
        self.cache_manager.handle_write(processor_id, slot_address, 0, self.cache_manager.memory)
        slot.occupied_by = None

    def check_slot(self, processor_id, slot_id, memory):
        slot_address = slot_id
        car_id, transaction = self.cache_manager.handle_read(processor_id, slot_address, memory)
        status = f"Ocupada por Carro {car_id}" if car_id else "Vaga Livre"
        print(f"Processador {processor_id} consulta Vaga {slot_id}: {status} ({transaction})")
    
    def move_car(self, processor_id, car_id, new_slot_id):
        current_slot = None
        for slot in self.parking_lot.slots:
            if slot.occupied_by and slot.occupied_by.id == car_id:
                current_slot = slot
                break
        
        if not current_slot:
            print(f"Erro: Carro {car_id} não está estacionado")
            return
        
        if current_slot.occupied_by.processor_id != processor_id:
            print(f"Erro: Somente o Processador {current_slot.occupied_by.processor_id} pode mover o Carro {car_id}")
            return

        new_slot = self.parking_lot.slots[new_slot_id]

        if new_slot.occupied_by:
            print(f"Erro: Vaga {new_slot_id} já está ocupada por Carro {new_slot.occupied_by.id}")
            return

        self.remove_car(processor_id, current_slot.id)
        self.park_car(processor_id, car_id, new_slot_id)

def test():

    tamanho_memoria = memoTamanho()
    tamanho_cache = cacheTamanho()
    
    memory = Memory(tamanho_memoria)
    cache_manager = CacheManager(memory)

    # Inicializa os processadores
    processor1 = Processor(1, tamanho_cache, memory, cache_manager)
    processor2 = Processor(2, tamanho_cache, memory, cache_manager)
    processor3 = Processor(3, tamanho_cache, memory, cache_manager)

    processors = [processor1, processor2, processor3]

    parking_lot = ParkingLot(tamanho_memoria)
    parking_manager = ParkingManager(parking_lot, cache_manager)

    parking_lot.print_slots()

    parking_manager.park_car(1, 101, 1)
    parking_manager.park_car(2,102,2)
    parking_manager.park_car(3,103,3)
    parking_manager.check_slot(1, 2,memory)
    parking_manager.check_slot(1, 10,memory)
    # parking_manager.park_car(1, 102, 2)
    # parking_manager.park_car(1, 103, 3)    
    # parking_manager.park_car(1, 104, 4)
    processor1.print_cache()
    memory.print_memory()
    # parking_manager.move_car(1, 101, 9)
    # parking_manager.park_car(1, 105, 5)
    # parking_manager.remove_car(1, 1)
    # parking_manager.park_car(2, 222,1)


    for p in processors:
        p.print_cache()

    memory.print_memory()
    parking_lot.print_slots()

def main():
    test()

if __name__ == "__main__":
    main()
