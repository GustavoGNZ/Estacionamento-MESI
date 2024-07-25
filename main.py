from memory import Memory
from cacheManager import CacheManager
from processor import Processor

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

def main():

    tamanho_memoria = memoTamanho()
    tamanho_cache = cacheTamanho()
    
    memory = Memory(tamanho_memoria)
    cache_manager = CacheManager()

    # Inicializa os processadores
    processor1 = Processor(1, tamanho_cache, memory, cache_manager)
    processor2 = Processor(2, tamanho_cache, memory, cache_manager)
    processor3 = Processor(3, tamanho_cache, memory, cache_manager)

    processors = [processor1, processor2, processor3]

if __name__ == "__main__":
    main()
