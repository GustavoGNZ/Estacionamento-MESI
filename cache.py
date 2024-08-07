from enum import Enum
import random

class State(Enum):
    """
    Enumeração que representa os possíveis estados de uma linha de cache.
    """
    MODIFIED = 'M'  # Estado modificado: A linha foi alterada e a cópia na memória principal está desatualizada.
    EXCLUSIVE = 'E' # Estado exclusivo: A linha está na cache e não está em nenhuma outra cache.
    SHARED = 'S'    # Estado compartilhado: A linha está presente em uma ou mais caches e não foi modificada.
    INVALID = 'I'   # Estado inválido: A linha não contém dados válidos.

class CacheLine:
    """
    Representa uma linha de cache.
    """
    def __init__(self):
        """
        Inicializa uma nova linha de cache com endereço, dados e estado como inválidos.
        """
        self.address = None
        self.data = None
        self.state = State.INVALID

    def update(self, address, data, state):
        """
        Atualiza o endereço, dados e estado da linha de cache.
        
        :param address: Endereço da linha de cache.
        :param data: Dados da linha de cache.
        :param state: Estado da linha de cache.
        """
        self.address = address
        self.data = data
        self.state = state

    def print_line(self, line_index):
        """
        Imprime as informações da linha de cache.
        
        :param line_index: Índice da linha de cache.
        """
        state = self.state.value if self.state else "N/A"
        print(f"Linha {line_index}: Endereço = {self.address}, Dado = {self.data}, Estado = {state}")

class Cache:
    """
    Representa um cache com um conjunto de linhas e controle de substituição FIFO.
    """
    def __init__(self, size):
        """
        Inicializa um cache com um tamanho específico e uma fila FIFO para controle de substituição de linhas.
        
        :param size: Número de linhas no cache.
        """
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = []  # FIFO para controle de substituição de linhas

    def search(self, address):
        """
        Procura uma linha de cache pelo endereço fornecido.
        
        :param address: Endereço para procurar.
        :return: A linha de cache correspondente ao endereço, ou None se não encontrada.
        """
        return next((line for line in self.lines if line.address == address), None)

    def write(self, address, data, state):
        """
        Escreve dados em uma linha de cache no endereço fornecido. Se o endereço já existe, atualiza a linha existente,
        caso contrário, substitui uma linha existente ou adiciona uma nova linha, se disponível.
        
        :param address: Endereço da linha de cache.
        :param data: Dados a serem escritos.
        :param state: Estado a ser definido para a linha de cache.
        :return: Uma tupla indicando o resultado da operação (código de operação, endereço removido, dados removidos).
        """
        line = self.search(address)
        if line:
            return self.update_existing_line(line, address, data)
        else:
            line = self.search(None)
            if line:
                empty_lines = [l for l in self.lines if l.address is None]
                if empty_lines:
                    line = random.choice(empty_lines)
                    line.update(address, data, state)
                    self.fifoQueue.append(self.lines.index(line))
                    return "WM", None, None
            elif self.is_full():
                return self.replace_line_in_cache(address, data, state)
        return "WM", None, None

    def update_existing_line(self, line, address, data):
        """
        Atualiza uma linha de cache existente com novos dados e estado.
        
        :param line: Linha de cache a ser atualizada.
        :param address: Endereço da linha de cache.
        :param data: Dados a serem atualizados.
        :return: Uma tupla indicando o resultado da operação (código de operação, endereço removido, dados removidos).
        """
        if line.state != State.INVALID:
            line.update(address, data, State.MODIFIED)
            return "WH", None, None

    def replace_line_in_cache(self, address, data, state):
        """
        Substitui uma linha de cache existente utilizando o algoritmo FIFO e escreve os novos dados.
        
        :param address: Endereço da nova linha de cache.
        :param data: Dados a serem escritos.
        :param state: Estado a ser definido para a nova linha de cache.
        :return: Uma tupla indicando o resultado da operação (código de operação, endereço removido, dados removidos).
        """
        index = self.fifoQueue.pop(0)
        line_to_remove = self.lines[index]
        address_to_remove, data_to_remove = line_to_remove.address, line_to_remove.data
        self.lines[index] = CacheLine()
        self.write(address, data, state)
        return "WM", address_to_remove, data_to_remove

    def update_state(self, address, new_state):
        """
        Atualiza o estado de uma linha de cache pelo endereço fornecido.
        
        :param address: Endereço da linha de cache.
        :param new_state: Novo estado a ser definido para a linha de cache.
        :return: True se a linha foi encontrada e o estado atualizado, False caso contrário.
        """
        line = self.search(address)
        if line:
            line.state = new_state
            return True

    def print_cache(self, processor_id):
        """
        Imprime o conteúdo do cache para o processador especificado.
        
        :param processor_id: ID do processador para o qual o cache está sendo impresso.
        """
        print(f"Cache do Processador {processor_id}:")
        for i, line in enumerate(self.lines):
            line.print_line(i)
        print()

    def is_full(self):
        """
        Verifica se o cache está cheio.
        
        :return: True se o cache estiver cheio, False caso contrário.
        """
        return all(line.address is not None for line in self.lines)
