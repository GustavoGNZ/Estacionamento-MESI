
from cache import Cache

class Processor:

    def __init__(self, processor_number, bus, memory):

        self.cache = Cache()
        self.processor_number = processor_number
        self.bus = bus
        self.memory = memory
        # self.bus.processors.append(self)


    def writeValue(self,address,value):

        if(self.cache.address == None):         #first time when the shared memory address block enter the cache of the processors

            if(self.bus.bus_snoop(self.processor_number,address)): # if there no copies of the shared memory address block

                self.cache.state = "E"
                self.cache.address = address
                self.cache.value = value
                self.memory.data[address] = value

            else:
                self.cache.state = "M"
                self.cache.address = address
                self.cache.value = value
                self.memory.status[address] = "dirty"

        elif(self.cache.address == address): # if we have copies of the address block

            if(self.cache.state == "S"): # if the cache status bit is 'S' change it to 'E'

                self.cache.state = "E"
                self.cache.value = value
                self.cache.address = address
                self.memory.data[address] = value
                self.bus.bus_snoop(self.processor_number,address)

            if (self.cache.state == "E"): # if the cache status bit is 'E' change it to 'M'

                self.cache.state = "M"
                self.cache.value = value
                self.cache.address = address

                if(self.memory.status[self.cache.address] == "clean"): # need to change the shared memory block address status as we are implementing WRITE BACK.
                    self.memory.status[self.cache.address] = "dirty"

                self.bus.bus_snoop(self.processor_number,address)

            if (self.cache.state == "M"): # if the cache status bit is 'M', we just update the value.

                self.cache.value = value
                self.cache.address = address
                self.bus.bus_snoop(self.processor_number,address)

        else: # need to replace the cache block with new shared memory address block.

            if(self.bus.bus_snoop(self.processor_number,address)):

                if(self.memory.status[self.cache.address] == "dirty" and self.cache.state != "I" ): # if the shared memory address block is dirty and
                    # cache status is either 'M' or 'E' or 'S', first we need to update the shared memory address block(WRITE BACK) and then copy the new value.

                    self.memory.data[self.cache.address] = self.cache.value
                    self.memory.status[self.cache.address] = "clean"


                self.memory.status[address] = "dirty"
                self.cache.state = "E"
                self.cache.value = value
                self.cache.address = address

            else:

                # we dont have an copies in other processor's cache, we just updated the shared memory address block and copy the value, change the cache's bit to 'm'
                self.memory.data[self.cache.address] = self.cache.value
                self.memory.status[self.cache.address] = "clean"

                self.cache.state = "M"
                self.cache.value = value
                self.cache.address = address
                self.memory.status[address] = "dirty"

        return

    def readValue(self,address):

        if (self.bus.read_bus_snoop(self.processor_number, address)):

            if(self.cache.state == "M"): # if the cache status bit is 'M', we need to WRITE BACK to the shared memory before we read the value and change the cache's status bit to 'S'.
                self.memory.data[self.cache.address] = self.cache.value
                self.memory.status[self.cache.address] = "clean"

            self.cache.state = "S"
            self.cache.address = address
            self.cache.value = self.memory.data[address]


        else:

            # if we are reading the value for the first time from the shared memory address block and don't have copies in any other processor's cache.
            if(self.cache.state == "M"):

                if(self.memory.status[self.cache.address] == "dirty"):

                    self.memory.data[self.cache.address] = self.cache.value
                    self.memory.status[self.cache.address]  = "clean"
                    self.cache.address = address
                    self.cache.value = self.memory.data[address]
                    self.cache.state = "E"
                return

            if(self.cache.state == "E"):

                self.cache.address = address
                self.cache.value = self.memory.data[address]
                return

            else:
                self.cache.state = "E"
                self.cache.address = address
                self.cache.value = self.memory.data[address]

        return
