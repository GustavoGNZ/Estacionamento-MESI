from enum import Enum
import random

class State(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'

class CacheLine:
    """
        Inicializa uma instância da linha de Cache.

        Atributos:
        - address: Endereço da linha.
        - data: Dado armazenado na linha.
        - state: Estado da linha.
    """
    def __init__(self):
        self.address = None
        self.data = None
        self.state = State.INVALID

    def update(self, address, data, state):
        self.address = address
        self.data = data
        self.state = state

    def print_line(self):
        print(f"Endereço = {self.address}, Dado = {self.data}, Estado = {self.state}")

class Cache:
    def __init__(self, size):
        """
        Inicializa uma instância da classe Cache.

        Parâmetros:
        - size (int): Tamanho da cache.

        Atributos:
        - lines (list): Lista de linhas da cache.
        - size (int): Tamanho da cache.
        - fifoQueue (list): Fila FIFO para controle de substituição de linhas.
        """
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = []

    def search(self, address):
        """
        Procura por uma linha na cache com o endereço especificado.

        Parâmetros:
        - address: Endereço a ser procurado.

        Retorna:
        - line: A linha da cache com o endereço especificado, se encontrada.
        - None: Caso contrário.
        """
        for line in self.lines:
            if line.address == address:
                return line
        return None

    def write(self, address, data, state):
        """
        Escreve um dado na cache com o endereço e estado especificados.

        Parâmetros:
        - address: Endereço do dado a ser escrito.
        - data: Dado a ser escrito.
        - state: Estado do dado a ser escrito.

        Retorna:
        - "WH": Se ocorrer um Write Hit (WH).
        - "WM": Se ocorrer um Write Miss (WM).
        - address_to_remove: Endereço da linha removida em caso de Write Miss (WM).
        - data_to_remove: Dado da linha removida em caso de Write Miss (WM).
        """
        line = self.search(address)
        if line:
            # Write Hit (WH)
            if line.state in [State.SHARED, State.MODIFIED, State.EXCLUSIVE]:
                line.update(address, data, State.MODIFIED)
                return "WH", None, None
        else:
            # Write Miss (WM)
            line = self.search(None)
            if line:
                empty_lines = [l for l in self.lines if l.address is None]
                if empty_lines:
                    line = random.choice(empty_lines)
                    line.update(address, data, state)
                    self.fifoQueue.append(self.lines.index(line))
                    return "WM", None, None
            elif self.is_full():
                index = self.fifoQueue.pop(0)
                line_to_remove = self.lines[index]
                address_to_remove = line_to_remove.address
                data_to_remove = line_to_remove.data
                self.lines[index] = CacheLine()
                self.write(address, data, state)
                return "WM", address_to_remove, data_to_remove

    def read(self, address, memory, cache_manager, processor_id):
        """
        Lê um dado da cache com o endereço especificado.

        Parâmetros:
        - address: Endereço do dado a ser lido.
        - memory: Instância da classe Memory.
        - cache_manager: Instância da classe CacheManager.
        - processor_id: ID do processador.

        Retorna:
        - data: Dado lido da cache ou da memória principal.
        - "RH": Se ocorrer um Read Hit (RH).
        - "RM": Se ocorrer um Read Miss (RM).
        """
        line = self.search(address)
        if line and line.state != State.INVALID:
            # Read Hit (RH)
            return line.data, "RH"
        else:
            # Read Miss (RM)
            data = memory.read(address)
            is_shared = cache_manager.is_shared(address, processor_id)
            new_state = State.SHARED if is_shared else State.EXCLUSIVE
            self.write(address, data, new_state)
            return data, "RM"

    def update_state(self, address, new_state):
        """
        Atualiza o estado de uma linha da cache com o endereço especificado.

        Parâmetros:
        - address: Endereço da linha a ser atualizada.
        - new_state: Novo estado da linha.
        """
        line = self.search(address)
        if line:
            line.state = new_state

    def print_cache(self, processor_id):
        """
        Imprime o conteúdo da cache do processador especificado.

        Parâmetros:
        - processor_id: ID do processador.
        """
        print(f"Cache do Processador {processor_id}:")
        for i, line in enumerate(self.lines):
            state = line.state.value if line.state else "N/A"
            print(f"Linha {i}: Endereço = {line.address}, Dado = {line.data}, Estado = {state}")
        print()

    def is_full(self):
        """
        Verifica se a cache está cheia.

        Retorna:
        - True: Se a cache estiver cheia.
        - False: Caso contrário.
        """
        return len(self.lines) >= self.size
