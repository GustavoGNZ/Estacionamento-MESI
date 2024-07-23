from cache import Cache

class CPU:
    def __init__(self, id, cache_size, cache_controller):
        self.id = id
        self.cache = Cache(cache_size)
        self.cache_controller = cache_controller
        self.cache_controller.register_cache(self.cache)

    def read_data(self, memory, address):
        data, state = self.cache.read_from_cache(address)
        if data is not None:
            print(f"Processador {self.id}: Read Hit (RH) - Estado: {state}")
            return data
        else:
            print(f"Processador {self.id}: Read Miss (RM)")
            line = self.cache_controller.read(self.id, address)
            if line:
                print(f"Processador {self.id}: Dado presente na cache de outro processador.")
                data = line.data
                self.cache.load_data_to_cache(address, data).state = 'S'
            else:
                data = memory.read(address)
                self.cache.load_data_to_cache(address, data)
            return data

    def write_data(self, memory, address, data):
        line = self.cache.write_to_cache(address, data)
        if line:
            if line.state == 'S':
                print(f"Processador {self.id}: Write Hit (WH) - Estado: {line.state}")
                self.cache_controller.write(self.id, address)
                line.state = 'M'
            elif line.state == 'E':
                print(f"Processador {self.id}: Write Hit (WH) - Estado: {line.state}")
                line.state = 'M'
            elif line.state == 'M':
                print(f"Processador {self.id}: Write Hit (WH) - Estado: {line.state}")
            return
        else:
            print(f"Processador {self.id}: Write Miss (WM)")
            self.cache_controller.write(self.id, address)
            memory.write(address, data)
            self.cache.load_data_to_cache(address, data).state = 'M'
