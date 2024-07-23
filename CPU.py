from memory import Memory
from processor import Processor

class CPU:

    #Class which maintains the Processing Unit of the four cores.

    def __init__(self):

        self.memory = Memory() #instance of the sharedMemory class

        # self.bus = Bus(self.memory)

        self.processors = {}
        for processor_number in range(4):
            self.processors= Processor(processor_number, self.bus, self.memory)

    def printStatus(self):

        print("Main Memory : ")
        print(self.bus.memory.data)
        print(" ")

        if(self.bus.instruction_processor != None):

            if(str(self.bus.instruction_type) == "reads"):

                print("Instruction -> Processor_" + str(self.bus.instruction_processor) + " " +
                      str(self.bus.instruction_type) + " from address:" + str(self.bus.instruction_address))
            else:
                print("Instruction -> Processor_" + str(self.bus.instruction_processor) + " " +
                  str(self.bus.instruction_type) + " " + "value:" + str(
                self.bus.instruction_value) + " to address:" + str(self.bus.instruction_address))

        print(" ")

        for processor in range(len(self.bus.processors)):
            print("Processor number: "+str(processor))
            print("Cache State: " + self.bus.processors[processor].cache.state)


            if(self.bus.processors[processor].cache.address == None):
                print("Cache memory address: " + "empty")
            else:
                print("Cache memory address: " + str(self.bus.processors[processor].cache.address))

            if (self.bus.processors[processor].cache.value == None):
                print("Cache memory value: " + "empty")
            else:
                print("Cache memory value: " + str(self.bus.processors[processor].cache.value))

            print(" ")

        print("*******************************************************************************")
