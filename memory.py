class Memory:
    def __init__(self, size):
        self.size = size
        self.data = [0 for _ in range(size)] # Inicializa a memória com 0s significando que as vagas estão vazias

    def read(self, address):
        return self.data[address]
    
    def write(self, address, data):
        self.data[address] = data

    def print_memory(self):
        print("Memória Principal:")
        for i, value in enumerate(self.data):
            print(f"Endereço {i}: {value}")
        print()