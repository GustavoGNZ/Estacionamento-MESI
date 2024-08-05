import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from enum import Enum
from memory import Memory
from cacheManager import CacheManager
from processor import Processor
from parking import ParkingLot
from parking import ParkingManager
import sys
import io

class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Estacionamento com Protocolo MESI")

        self.memory = Memory(50)
        self.cache_manager = CacheManager(self.memory)
        self.parking_lot = ParkingLot(10)
        self.parking_manager = ParkingManager(self.parking_lot, self.cache_manager)

        self.processor1 = Processor(1, 5, self.memory, self.cache_manager)
        self.processor2 = Processor(2, 5, self.memory, self.cache_manager)
        self.processor3 = Processor(3, 5, self.memory, self.cache_manager)
        self.processors = [self.processor1, self.processor2, self.processor3]

        self.selected_processor = None

        self.create_widgets()

    def create_widgets(self):
        self.processor_label = ttk.Label(self.root, text="Processador atual: Nenhum")
        self.processor_label.grid(row=0, column=0, columnspan=2, pady=5)

        self.select_processor_button = ttk.Button(self.root, text="Selecionar Processador", command=self.select_processor)
        self.select_processor_button.grid(row=1, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.check_slot_button = ttk.Button(self.root, text="Verificar Vagas (Leitura)", command=self.check_slot)
        self.check_slot_button.grid(row=2, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.park_car_button = ttk.Button(self.root, text="Estacionar Carro (Escrita)", command=self.park_car)
        self.park_car_button.grid(row=3, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.remove_car_button = ttk.Button(self.root, text="Remover Carro (Escrita)", command=self.remove_car)
        self.remove_car_button.grid(row=4, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.move_car_button = ttk.Button(self.root, text="Mudar Carro de Vaga (Escrita)", command=self.move_car)
        self.move_car_button.grid(row=5, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.show_status_button = ttk.Button(self.root, text="Mostrar estado da cache e da memória", command=self.show_status)
        self.show_status_button.grid(row=6, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.show_parking_slots_button = ttk.Button(self.root, text="Mostrar Vagas do Estacionamento", command=self.show_parking_slots)
        self.show_parking_slots_button.grid(row=7, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.clear_output_button = ttk.Button(self.root, text="Limpar Entrada de Texto", command=self.clear_output)
        self.clear_output_button.grid(row=8, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.quit_button = ttk.Button(self.root, text="Sair", command=self.root.quit)
        self.quit_button.grid(row=9, column=0, columnspan=2, pady=5,sticky=tk.W)

        self.output_text = tk.Text(self.root, wrap="word", height=15, width=60)
        self.output_text.grid(row=10, column=0, columnspan=2, pady=5, padx=5)
        self.output_text.config(state=tk.DISABLED)

    def select_processor(self):
        processor_id = int(tk.simpledialog.askstring("Selecionar Processador", "Digite o ID do processador:"))
        self.selected_processor = None
        for processor in self.processors:
            if processor.id == processor_id:
                self.selected_processor = processor
                break
        if self.selected_processor is None:
            messagebox.showerror("Erro", "Processador não encontrado.")
        else:
            self.processor_label.config(text=f"Processador atual: {self.selected_processor.id}")

    def check_slot(self):
        if self.selected_processor is None:
            messagebox.showerror("Erro", "Nenhum processador selecionado.")
            return
        vaga = int(tk.simpledialog.askstring("Verificar Vaga", "Qual vaga você quer verificar se está vazia?"))
        result = self.parking_manager.check_slot(self.selected_processor.id, vaga)
        self.show_output(result)

    def park_car(self):
        if self.selected_processor is None:
            messagebox.showerror("Erro", "Nenhum processador selecionado.")
            return
        id_carro = int(tk.simpledialog.askstring("Estacionar Carro", "Digite o ID do carro:"))
        id_vaga = int(tk.simpledialog.askstring("Estacionar Carro", "Digite o ID da vaga:"))
        result = self.parking_manager.park_car(self.selected_processor.id, id_carro, id_vaga)
        self.show_output(result)

    def remove_car(self):
        if self.selected_processor is None:
            messagebox.showerror("Erro", "Nenhum processador selecionado.")
            return
        id_vaga = int(tk.simpledialog.askstring("Remover Carro", "Digite o ID da vaga:"))
        result = self.parking_manager.remove_car(self.selected_processor.id, id_vaga)
        self.show_output(result)

    def move_car(self):
        if self.selected_processor is None:
            messagebox.showerror("Erro", "Nenhum processador selecionado.")
            return
        id_vaga = int(tk.simpledialog.askstring("Mudar Carro de Vaga", "Digite o ID da vaga:"))
        id_vaga_destino = int(tk.simpledialog.askstring("Mudar Carro de Vaga", "Digite o ID da vaga de destino:"))
        result = self.parking_manager.move_car(self.selected_processor.id, id_vaga, id_vaga_destino)
        self.show_output(result)

    def show_parking_slots(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        output = "Estado das Vagas no Estacionamento:\n\n"
        output += self.parking_lot.print_slots()  # Chama o método print_slots da classe ParkingLot
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def show_status(self):
        old_stdout = sys.stdout
        result = io.StringIO()
        sys.stdout = result

        for processor in self.processors:
            processor.print_cache()
        self.memory.print_memory()

        output = result.getvalue()
        sys.stdout = old_stdout
        self.show_output(output)

    def show_output(self, output):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
