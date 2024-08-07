from cache import CacheLine, State

class CacheManager:
    """
    Gerencia múltiplos caches de processadores e controla a comunicação entre eles e a memória principal.
    """
    def __init__(self, memory):
        """
        Inicializa o gerenciador de cache com a memória principal.

        :param memory: Instância do componente de memória principal.
        """
        self.caches = {}
        self.memory = memory

    def register_cache(self, processor_id, cache):
        """
        Registra um cache para um processador específico.

        :param processor_id: Identificador do processador.
        :param cache: Instância do cache a ser registrada.
        """
        self.caches[processor_id] = cache

    def get_cache(self, processor_id):
        """
        Obtém o cache associado a um processador específico.

        :param processor_id: Identificador do processador.
        :return: Instância do cache associado ao processador ou None se não encontrado.
        """
        return self.caches.get(processor_id)

    def invalidate_other_caches(self, address, excluding_processor_id):
        """
        Invalida as linhas de cache em todos os caches, exceto no cache do processador especificado.

        :param address: Endereço da linha de cache a ser invalidada.
        :param excluding_processor_id: Identificador do processador cujo cache não deve ser invalidado.
        """
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                cache.update_state(address, State.INVALID)

    def is_shared(self, address, excluding_processor_id):
        """
        Verifica se o endereço é compartilhado entre caches, excluindo o cache do processador especificado.

        :param address: Endereço a ser verificado.
        :param excluding_processor_id: Identificador do processador cujo cache não deve ser considerado.
        :return: True se o endereço for compartilhado em outros caches, False caso contrário.
        """
        return any(self.is_line_shared(pid, address) for pid in self.caches if pid != excluding_processor_id)

    def is_line_shared(self, processor_id, address):
        """
        Verifica se a linha de cache com o endereço especificado está compartilhada no cache do processador dado.

        :param processor_id: Identificador do processador.
        :param address: Endereço da linha de cache.
        :return: True se a linha de cache está compartilhada (estado SHARED, EXCLUSIVE ou MODIFIED), False caso contrário.
        """
        line = self.caches[processor_id].search(address)
        return line and line.state in {State.SHARED, State.EXCLUSIVE, State.MODIFIED}

    def update_state_to_shared_if_exclusive(self, address, excluding_processor_id):
        """
        Atualiza o estado de linhas de cache para SHARED se estiverem em EXCLUSIVE em caches de processadores,
        excluindo o processador especificado.

        :param address: Endereço da linha de cache.
        :param excluding_processor_id: Identificador do processador cujo cache não deve ser atualizado.
        """
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, address, memory):
        """
        Processa uma operação de leitura para o endereço especificado. Atualiza os caches e a memória principal conforme necessário.

        :param processor_id: Identificador do processador que está realizando a leitura.
        :param address: Endereço a ser lido.
        :param memory: Instância do componente de memória principal.
        :return: Dados lidos e um código de operação ('RH' para leitura do cache ou 'RM' para leitura da memória).
        """
        def update_all_caches(self, address, data, processor_id):
            """
            Atualiza todos os caches com os novos dados e estados.

            :param address: Endereço da linha de cache.
            :param data: Dados a serem atualizados.
            :param processor_id: Identificador do processador que está realizando a operação.
            """
            is_shared = self.is_shared(address, processor_id)
            new_state = State.SHARED if is_shared else State.EXCLUSIVE
            state, add_to_memory, data_to_memory = self.caches[processor_id].write(address, data, new_state)
            for cache in self.caches.values():
                if cache.search(address):
                    cache.update_state(address, new_state)
            self.update_state_to_shared_if_exclusive(address, processor_id)

            if add_to_memory is not None and data_to_memory is not None:
                memory.write(add_to_memory, data_to_memory)

        # Verificar se o dado está presente em qualquer cache
        for pid, cache in self.caches.items():
            line = cache.search(address)
            if line and line.state != State.INVALID:
                # Dado encontrado em outra cache
                print(f"Processador {processor_id} lê o endereço {address} com dado {line.data} ({'RH'})")
                if self.caches[processor_id].update_state(address, State.SHARED) != True:
                    state, add_to_memory, data_to_memory = self.caches[processor_id].write(address, line.data, State.SHARED)
                    if add_to_memory is not None and data_to_memory is not None:
                        memory.write(add_to_memory, data_to_memory)
                update_all_caches(self, address, line.data, processor_id)
                return line.data, 'RH'

        # Cache Miss: Read from memory and update all caches
        data = memory.read(address)
        is_shared = self.is_shared(address, processor_id)

        update_all_caches(self, address, data, processor_id)

        print(f"Processador {processor_id} lê o endereço {address} com dado {data} ({'RM'})")
        return data, 'RM'

    def handle_write(self, processor_id, address, data, memory):
        """
        Processa uma operação de escrita para o endereço especificado. Invalida outras caches e atualiza a memória principal conforme necessário.

        :param processor_id: Identificador do processador que está realizando a escrita.
        :param address: Endereço a ser escrito.
        :param data: Dados a serem escritos.
        :param memory: Instância do componente de memória principal.
        :return: Código de operação ('WM' para escrita na memória e 'WH' para escrita no cache).
        """
        self.invalidate_other_caches(address, processor_id)
        cache = self.get_cache(processor_id)
        transaction, old_address, old_data = cache.write(address, data, State.MODIFIED)
        if data == 0:
            memory.write(address, data)
        if transaction == 'WM' and old_address is not None and old_data is not None:
            memory.write(old_address, old_data)
        return transaction
