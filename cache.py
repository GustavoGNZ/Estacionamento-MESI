from enum import Enum
import random

class State(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'

class CacheLine:
    def __init__(self):
        self.address = None
        self.data = None
        self.state = State.INVALID

    def update(self, address, data, state):
        self.address = address
        self.data = data
        self.state = state

    def print_line(self, line_index):
        state = self.state.value if self.state else "N/A"
        print(f"Linha {line_index}: Endereço = {self.address}, Dado = {self.data}, Estado = {state}")

class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size
        self.fifoQueue = [] # FIFO para controle de substituição de linhas

    def search(self, address):
        return next((line for line in self.lines if line.address == address), None)

    def write(self, address, data, state):
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
        # return self.add_or_replace_line(address, data, state)

    def update_existing_line(self, line, address, data):
        if line.state != State.INVALID: # substituir para != INVALID
            line.update(address, data, State.MODIFIED)
            return "WH", None, None

    def replace_line_in_cache(self, address, data, state):
        index = self.fifoQueue.pop(0)
        line_to_remove = self.lines[index]
        address_to_remove, data_to_remove = line_to_remove.address, line_to_remove.data
        self.lines[index] = CacheLine()
        self.write(address, data, state)
        return "WM", address_to_remove, data_to_remove

    def update_state(self, address, new_state):
        line = self.search(address)
        if line:
            line.state = new_state
            return True

    def print_cache(self, processor_id):
        print(f"Cache do Processador {processor_id}:")
        for i, line in enumerate(self.lines):
            line.print_line(i)
        print()

    def is_full(self):
        return all(line.address is not None for line in self.lines)