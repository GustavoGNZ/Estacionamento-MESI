from cache import CacheLine, State

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

    def update_state_to_shared_if_exclusive(self, address, excluding_processor_id):
        for pid, cache in self.caches.items():
            if pid != excluding_processor_id:
                line = cache.search(address)
                if line and line.state == State.EXCLUSIVE:
                    line.state = State.SHARED

    def handle_read(self, processor_id, address, memory):

        def update_all_caches(self, address, data, processor_id):
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

        # Atualizar todos os caches com o novo estado

        print(f"Processador {processor_id} lê o endereço {address} com dado {data} ({'RM'})")
        return data, 'RM'

    def handle_write(self, processor_id, address, data, memory):
        self.invalidate_other_caches(address, processor_id)
        cache = self.get_cache(processor_id)
        transaction, old_address, old_data = cache.write(address, data, State.MODIFIED)
        if data == 0:
            memory.write(address, data)
        if transaction == 'WM' and old_address is not None and old_data is not None:
            memory.write(old_address, old_data)
        return transaction

