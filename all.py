from enum import Enum
import random

class Memory:  # Memoria Ram
    def __init__(self, size):
        self.size = size
        self.data = [random.randint(1000, 9999) for _ in range(size)]

    def read(self, address):
        return self.data[address]

    def write(self, address, value):
        self.data[address] = value


class State(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'


class CacheLine:
    def __init__(self):
        self.tag = None
        self.data = None
        self.state = State.INVALID


class Cache:
    def __init__(self, size):
        self.lines = [CacheLine() for _ in range(size)]
        self.size = size

    def get_tag(self, address):
        return address // self.size

    def find_line(self, tag):
        for line in self.lines:
            if line.tag == tag:
                return line
        return None

    def replace_line(self, tag, data, state):
        for line in self.lines:
            if line.state == State.INVALID:
                line.tag = tag
                line.data = data
                line.state = state
                return line
        # FIFO replacement policy
        line = self.lines.pop(0)
        self.lines.append(line)
        line.tag = tag
        line.data = data
        line.state = state
        return line

    def add_line(self, tag, data, state):
        line = self.replace_line(tag, data, state)
        return line


class Processor:
    def __init__(self, processor_number, memory, cache_size):
        self.processor_number = processor_number
        self.memory = memory
        self.cache = Cache(cache_size)

    def read(self, address, processors):
        tag = self.cache.get_tag(address)
        line = self.cache.find_line(tag)
        if line:
            if line.state != State.INVALID:
                # Cache hit (RH)
                return 'RH', line.data
            else:
                # Line is invalid, need to read from memory and validate
                data = self.memory.read(address)
                if self.is_line_in_other_processors(tag, processors):
                    line.state = State.SHARED
                else:
                    line.state = State.EXCLUSIVE
                line.data = data
                return 'RM', data
        else:
            # Cache miss (RM)
            data = self.memory.read(address)
            if self.is_line_in_other_processors(tag, processors):
                self.cache.add_line(tag, data, State.SHARED)
            else:
                self.cache.add_line(tag, data, State.EXCLUSIVE)
            return 'RM', data

    def write(self, address, value, processors):
        tag = self.cache.get_tag(address)
        line = self.cache.find_line(tag)
        if line:
            if line.state != State.INVALID:
                # Cache hit and write (WH)
                line.data = value
                line.state = State.MODIFIED
                self.invalidate_other_caches(tag, processors)
                return 'WH'
        # Cache miss or invalid state, write to memory and cache (WM)
        self.memory.write(address, value)
        if self.is_line_in_other_processors(tag, processors):
            line = self.cache.add_line(tag, value, State.MODIFIED)
            self.invalidate_other_caches(tag, processors)
        else:
            line = self.cache.add_line(tag, value, State.MODIFIED)
        return 'WM'

    def is_line_in_other_processors(self, tag, processors):
        """
        Verifica se algum outro processador tem a linha de cache especificada.
        """
        return any(proc.cache.find_line(tag) for proc in processors if proc != self)

    def invalidate_other_caches(self, tag, processors):
        """
        Invalida a linha de cache especificada em todos os outros processadores.
        """
        for processor in processors:
            if processor != self:
                line = processor.cache.find_line(tag)
                if line and line.state != State.INVALID:
                    line.state = State.INVALID


class Simulador:
    def __init__(self, num_processors, cache_size, memory_size):
        self.memory = Memory(memory_size)  # Memoria Compartilhada
        self.processors = [Processor(i, self.memory, cache_size) for i in range(num_processors)]  # 3 processadores


class CPU:
    def __init__(self, num_processors, cache_size, memory_size):
        self.simulador = Simulador(num_processors, cache_size, memory_size)

    def read(self, processor_number, address):
        processor = self.simulador.processors[processor_number]
        result = processor.read(address, self.simulador.processors)
        return result

    def write(self, processor_number, address, value):
        processor = self.simulador.processors[processor_number]
        result = processor.write(address, value, self.simulador.processors)
        return result
    
# Função principal para interação com o usuário
def main():
    num_processors = 3
    cache_size = 5
    memory_size = 50

    cpu = CPU(num_processors, cache_size, memory_size)

    while True:
        print("\nEscolha uma opção:")
        print("1. Ler valor")
        print("2. Escrever valor")
        print("3. Sair")

        choice = input("Digite o número da opção: ")

        if choice == '3':
            break

        processor_number = int(input("Digite o número do processador (0, 1 ou 2): "))
        address = int(input("Digite o endereço de memória: "))

        if choice == '1':
            result = cpu.read(processor_number, address)
            print(f"Resultado da leitura: {result[0]} - Valor: {result[1]}")
        elif choice == '2':
            value = int(input("Digite o valor a ser escrito: "))
            result = cpu.write(processor_number, address, value)
            print(f"Resultado da escrita: {result}")
        else:
            print("Opção inválida")

if __name__ == "__main__":
    main()