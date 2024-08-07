class Memory:
    """
    Representa a memória principal de um sistema com um tamanho fixo e operações de leitura e escrita.
    """
    def __init__(self, size):
        """
        Inicializa a memória com um tamanho específico e preenche com zeros.

        :param size: Tamanho da memória (número de endereços).
        """
        self.size = size
        self.data = [0 for _ in range(size)]  # Inicializa a memória com 0s

    def read(self, address):
        """
        Lê o valor armazenado no endereço especificado.

        :param address: Endereço da memória a ser lido.
        :return: Valor armazenado no endereço especificado.
        :raises IndexError: Se o endereço estiver fora dos limites da memória.
        """
        return self.data[address]
    
    def write(self, address, data):
        """
        Escreve um valor no endereço especificado.

        :param address: Endereço da memória onde o valor será escrito.
        :param data: Valor a ser escrito no endereço especificado.
        :raises IndexError: Se o endereço estiver fora dos limites da memória.
        """
        self.data[address] = data

    def print_memory(self):
        """
        Imprime o conteúdo da memória principal, mostrando o valor de cada endereço.
        """
        print("Memória Principal:")
        for i, value in enumerate(self.data):
            print(f"Endereço {i}: {value}")
        print()
