from cache import State

class CacheManager:
    """
    Gerenciador de Cache.

    Esta classe é responsável por gerenciar múltiplos caches associados a diferentes processadores.
    Ela fornece métodos para registrar caches, obter caches, invalidar caches, verificar se um dado está compartilhado,
    atualizar o estado para compartilhado, lidar com leituras e lidar com escritas.

    Atributos:
        caches (dict): Um dicionário que mapeia o ID do processador para o cache correspondente.

    Métodos:
        register_cache(processor_id, cache): Registra um cache associado a um processador.
        get_cache(processor_id): Retorna o cache associado a um processador.
        invalidate_other_caches(address, excluding_processor_id): Invalida os caches, exceto o cache do processador especificado.
        is_shared(address, excluding_processor_id): Verifica se um dado está compartilhado entre os caches, excluindo o cache do processador especificado.
        update_state_to_shared(address, excluding_processor_id): Atualiza o estado de um dado para compartilhado em todos os caches, excluindo o cache do processador especificado.
        handle_read(processor_id, address, memory): Lida com uma operação de leitura de um dado em um processador específico.
        handle_write(processor_id, address, data, memory): Lida com uma operação de escrita de um dado em um processador específico.
    """

    def __init__(self):
        self.caches = {}

    def register_cache(self, processor_id, cache):
        """
        Registra um cache associado a um processador.

        Args:
            processor_id (int): O ID do processador.
            cache (Cache): O cache a ser registrado.

        Returns:
            None
        """
        self.caches[processor_id] = cache

    def get_cache(self, processor_id):
        """
        Retorna o cache associado a um processador.

        Args:
            processor_id (int): O ID do processador.

        Returns:
            Cache: O cache associado ao processador.
        """
        return self.caches.get(processor_id)

    def invalidate_other_caches(self, address, excluding_processor_id):
        """
        Invalida os caches, exceto o cache do processador especificado.

        Args:
            address (int): O endereço do dado a ser invalidado.
            excluding_processor_id (int): O ID do processador cujo cache não deve ser invalidado.

        Returns:
            None
        """
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                cache.update_state(address, State.INVALID)

    def is_shared(self, address, excluding_processor_id):
        """
        Verifica se um dado está compartilhado entre os caches, excluindo o cache do processador especificado.

        Args:
            address (int): O endereço do dado a ser verificado.
            excluding_processor_id (int): O ID do processador cujo cache não deve ser considerado.

        Returns:
            bool: True se o dado está compartilhado, False caso contrário.
        """
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state in {State.SHARED, State.EXCLUSIVE, State.MODIFIED}:
                    return True
        return False

    def update_state_to_shared(self, address, excluding_processor_id):
        """
        Atualiza o estado de um dado para compartilhado em todos os caches, excluindo o cache do processador especificado.

        Args:
            address (int): O endereço do dado a ser atualizado.
            excluding_processor_id (int): O ID do processador cujo cache não deve ser atualizado.

        Returns:
            None
        """
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, address, memory):
        """
        Lida com uma operação de leitura de um dado em um processador específico.

        Args:
            processor_id (int): O ID do processador.
            address (int): O endereço do dado a ser lido.
            memory (Memory): A memória principal.

        Returns:
            tuple: Uma tupla contendo o dado lido e a transação realizada.
        """
        for pid, cache in self.caches.items():
            line = cache.search(address)
            if line and line.state != State.INVALID:
                if line.state == State.MODIFIED and pid != processor_id:
                    # Escreve os dados modificados na memória
                    memory.write(address, line.data)
                    # Atualiza o estado para compartilhado
                    self.update_state_to_shared(address, processor_id)
                    # Escreve os dados no cache do processador solicitante
                    self.caches[processor_id].write(address, line.data, State.SHARED)
                    # Atualiza o estado do cache que respondeu para compartilhado
                    line.state = State.SHARED
                    return line.data, "RH"
                if line.state == State.EXCLUSIVE and pid != processor_id:
                    self.update_state_to_shared(address, processor_id)
                    self.caches[processor_id].write(address, line.data, State.SHARED)
                    return line.data, "RH"
        # Se nenhum cache possui o dado, lê da memória
        data, transaction = self.caches[processor_id].read(address, memory, self, processor_id)
        return data, transaction

    def handle_write(self, processor_id, address, data, memory):
        """
        Lida com uma operação de escrita de um dado em um processador específico.

        Args:
            processor_id (int): O ID do processador.
            address (int): O endereço do dado a ser escrito.
            data: Os dados a serem escritos.
            memory (Memory): A memória principal.

        Returns:
            str: A transação realizada.
        """
        self.invalidate_other_caches(address, processor_id)
        cache = self.get_cache(processor_id)
        transaction, old_address, old_data = cache.write(address, data, State.MODIFIED)
        if transaction == 'WM' and old_address is not None and old_data is not None:
            memory.write(old_address, old_data)
        return transaction
