class CacheLine:
    def __init__(self):
        self.tag = None
        self.data = None
        self.state = 'I'  # Estados: M (modificado), E (exclusivo), S (compartilhado), I (inválido)

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size

    def map_to_cache_line(self, address):
        return address % self.size

    def check_cache(self, address):
        for line in self.lines:
            if line.tag == address:
                return line
        return None

    def load_data_to_cache(self, address, data):
        cache_line_index = self.map_to_cache_line(address)
        
        # Verifica se há uma linha de cache que será substituída
        if self.lines[cache_line_index].tag is not None:
            print(f"Substituindo linha da cache - Endereço {self.lines[cache_line_index].tag}")

        # Carrega o novo dado na linha de cache
        self.lines[cache_line_index].tag = address
        self.lines[cache_line_index].data = data
        self.lines[cache_line_index].state = 'E'  # Estado inicial como exclusivo
        return self.lines[cache_line_index]

    def read_from_cache(self, address):
        line = self.check_cache(address)
        if line and line.state != 'I':
            return line.data, line.state
        return None, None

    def write_to_cache(self, address, data):
        line = self.check_cache(address)
        if line:
            line.data = data
            line.state = 'M'
            return line
        return None

    def invalidate_cache(self, address):
        for line in self.lines:
            if line.tag == address:
                line.state = 'I'

class CacheController:
    def __init__(self, num_processors):
        self.caches = []

    def register_cache(self, cache):
        self.caches.append(cache)

    def read(self, processor_id, address):
        for i, cache in enumerate(self.caches):
            if i != processor_id:
                line = cache.check_cache(address)
                if line and line.state != 'I':
                    return line
        return None

    def write(self, processor_id, address):
        for i, cache in enumerate(self.caches):
            if i != processor_id:
                line = cache.check_cache(address)
                if line and line.state != 'I':
                    line.state = 'I'
