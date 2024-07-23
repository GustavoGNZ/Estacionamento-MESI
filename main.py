import random
from simulador import Simulador

def fill_memory(memory, size):
    memory.data = [random.randint(1000, 9999) for _ in range(size)]
    print("Memória principal preenchida com valores aleatórios.")

def display_memory(memory):
    print("\nMemória Principal:")
    for address, value in enumerate(memory.data):
        print(f"Endereço {address}: {value}")

def display_cache(processors):
    for processor in processors:
        print(f"\nCache do Processador {processor.id + 1}:")
        for idx, line in enumerate(processor.cache.lines):
            state = line.state if line.tag is not None else 'I'
            print(f"Linha {idx} - Tag: {line.tag}, Dado: {line.data}, Estado: {state}")

def user_interaction(simulator):
    while True:
        print("\nSelecione uma opção:")
        print("1. Ler dado da memória")
        print("2. Escrever dado na memória")
        print("3. Exibir memória principal")
        print("4. Exibir caches")
        print("0. Sair")
        choice = input("Opção: ")

        if choice == '0':
            print("Saindo...")
            break
    
        if choice == '1':
            processor_id = int(input("\nEscolha um processador (1-3): ")) - 1
            address = int(input("Digite o endereço da memória para leitura (0-49): "))
            data = simulator.read_data(processor_id, address)
            print(f"Dado lido do endereço {address}: {data}")

        elif choice == '2':
            processor_id = int(input("\nEscolha um processador (1-3): ")) - 1
            address = int(input("Digite o endereço da memória para escrita (0-49): "))
            data = int(input("Digite o dado para escrita: "))
            simulator.write_data(processor_id, address, data)
            print(f"Dado {data} escrito no endereço {address}.")

        elif choice == '3':
            display_memory(simulator.memory)

        elif choice == '4':
            display_cache(simulator.processors)

        else:
            print("Opção inválida. Tente novamente.")

def main():
    simulator = Simulador(num_processors=3, cache_size=5, memory_size=50)
    fill_memory(simulator.memory, simulator.memory.size)
    print("Sistema inicializado. Memória principal preenchida com valores aleatórios.")

    user_interaction(simulator)

if __name__ == "__main__":
    main()
