def get_size(prompt, min_size):
    tamanho = int(input(f"{prompt} (minimo {min_size}): "))
    if tamanho < min_size:
        print("Tamanho inválido, digite novamente")
        return get_size(prompt, min_size)
    return tamanho

def get_memory_size():
    return get_size("Digite o tamanho da memória", 50)

def get_cache_size():
    return get_size("Digite o tamanho da cache", 5)