import random

class Memory:
    """
    Classe que representa a memória principal.

    Atributos:
        size (int): O tamanho da memória.
        data (list): Uma lista que armazena os dados da memória.

    Métodos:
        read(address): Retorna o valor armazenado no endereço especificado.
        write(address, data): Escreve o valor especificado no endereço especificado.
        print_memory(): Imprime o conteúdo da memória.
    """

    def __init__(self, size):
        self.size = size
        self.data = [random.randint(1000, 9999) for _ in range(size)]

    def read(self, address):
        return self.data[address]
    
    def write(self, address, data):
        self.data[address] = data

    def print_memory(self):
        print("Memória Principal:")
        for i, value in enumerate(self.data):
            print(f"Endereço {i}: {value}")
        print()
