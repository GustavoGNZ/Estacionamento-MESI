from cacheManager import CacheManager
from cache import Cache

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

