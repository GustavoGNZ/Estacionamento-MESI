from enum import Enum
from memory import Memory
from cacheManager import CacheManager
from processor import Processor
from parking import ParkingLot
from parking import ParkingManager
from interface import get_memory_size, get_cache_size

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

    parking_lot = ParkingLot(tamanho_memoria)  # Tamanho do estacionamento
    parking_manager = ParkingManager(parking_lot, cache_manager)

    


def main():
    test()

if __name__ == "__main__":
    main()

