

class Car:
    def __init__(self, id):
        self.id = id
        self.processor_id = None

class ParkingSlot:
    def __init__(self, id):
        self.id = id
        self.occupied_by = None
    
    def is_occupied(self):
        return self.occupied_by is not None

    def is_occupied_by(self, car_id):
        return self.occupied_by and self.occupied_by.id == car_id

class ParkingLot:
    def __init__(self, size):
        self.slots = [ParkingSlot(i) for i in range(size)]

    def print_slots(self):
        status = "Estado das Vagas:\n"
        for slot in self.slots:
            car_id = slot.occupied_by.id if slot.occupied_by else "Nenhum"
            status += f"Vaga {slot.id}: Ocupada por Carro {car_id}\n" if slot.occupied_by else f"Vaga {slot.id}: Vaga Livre\n"
        return status

    def is_car_parked(self, car_id):
        for slot in self.slots:
            if slot.occupied_by and slot.occupied_by.id == car_id:
                return True
        return False
    
    def is_slot_free(self, slot_id):
        return not self.slots[slot_id].is_occupied()
    
    def is_slot_occupied_by_car(self, slot_id, car_id):
        return self.slots[slot_id].is_occupied_by(car_id)

class ParkingManager:
    def __init__(self, parking_lot, cache_manager):
        self.parking_lot = parking_lot
        self.cache_manager = cache_manager

    def park_car(self, processor_id, car_id, slot_id):
        texto = ""
        if self.parking_lot.is_car_parked(car_id):
            texto = (f"Erro: Carro {car_id} já está estacionado em outra vaga")
            return texto
            

        if not self.parking_lot.is_slot_free(slot_id):
            texto = (f"Erro: Vaga {slot_id} já está ocupada pelo carro {self.parking_lot.slots[slot_id].occupied_by.id}")
            return texto
            

        transaction = self.perform_park_car(processor_id, car_id, slot_id)
        texto = (f"Carro {car_id} estacionado na Vaga {slot_id} pelo Processador {processor_id}  {transaction}")
        return texto

    def perform_park_car(self, processor_id, car_id, slot_id):
        car = Car(car_id)
        car.processor_id = processor_id
        slot_address = slot_id
        transaction = self.cache_manager.handle_write(processor_id, slot_address, car.id, self.cache_manager.memory)

        self.parking_lot.slots[slot_id].occupied_by = car
        return transaction

    def remove_car(self, processor_id, slot_id):
        slot = self.parking_lot.slots[slot_id]
        if slot.is_occupied():
            if slot.occupied_by.processor_id == processor_id:
                texto = self.perform_remove_car(processor_id, slot_id)
            else:
                texto = (f"Erro: Somente o Processador {slot.occupied_by.processor_id} pode remover o Carro {slot.occupied_by.id}")
                return texto
        else:
            texto = (f"Erro: Vaga {slot_id} já está livre")
        
        return texto
        
    def perform_remove_car(self, processor_id, slot_id):
        transaction = self.cache_manager.handle_write(processor_id, slot_id, 0, self.cache_manager.memory)
        self.parking_lot.slots[slot_id].occupied_by = None
        texto = (f"Carro removido da Vaga {slot_id} pelo Processador {processor_id} - {transaction}")
        return texto

    def check_slot(self, processor_id, slot_id):
        car_id, transaction = self.cache_manager.handle_read(processor_id, slot_id, self.cache_manager.memory)
        status = f"Ocupada por Carro {car_id}" if car_id != 0 else "Livre"
        texto = (f"Vaga {slot_id} está {status} {transaction}")
        return texto


    def move_car(self, processor_id, from_slot_id, to_slot_id):
        car = self.parking_lot.slots[from_slot_id].occupied_by
        if not car:
            texto = (f"Erro: Vaga {from_slot_id} está livre")
            return texto
        if self.parking_lot.slots[to_slot_id].occupied_by:
            texto = (f"Erro: Vaga {to_slot_id} já está ocupada")
            return texto
        if car.processor_id == processor_id:
            self.remove_car(processor_id, from_slot_id)
            self.park_car(processor_id, car.id, to_slot_id)
            return "Carro alterado de vaga"
        
        texto = (f"Erro: Somente o Processador {self.parking_lot.slots[from_slot_id].occupied_by.processor_id} pode remover o Carro {self.parking_lot.slots[from_slot_id].occupied_by.id}")
        return texto
        