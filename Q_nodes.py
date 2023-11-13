import Q_particles
import Q_schedule
from functools import partial
import random

class node_NV:
    
    comm = None
    memSize = 1
    mem = [None]
    
    # while time units can be anything (as long as it is used consistently)
    # let's say time units are microseconds
    time_coh_comm = 20.0
    time_coh_mem = 120.0
    time_generate = 1.0
    time_swap = 2.50
    time_feedFwrd = 2.50
    time_reset = 2.0
    temperature = 1.0
    schedule = None

    def __init__(self, mS = 1, gT = 1.0, sT = 2.5, sch=None):
        self.comm = None
        self.memSize = mS
        self.mem = []
        for i in range(mS):
            self.mem.append(None)
        
        # set times
        self.time_generate = gT
        self.time_swap = sT
        self.time_feedFwrd = 2.50

        self.schedule = sch

    # comm qubit functions

    def generate(self):
        self.comm = Q_particles.particle()
        
        # add "decohere particle" to scheduler
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_coh_comm, 
                          partial(self.decohere_comm, self.comm))
        print(f"Queued decohere_comm - id:{self.comm.id}")
        return self.comm.id
    
    def decohere_comm(self, particle):
        if self.comm == None:
            print(f"decohere_comm - no comm found (searchID:{particle.id}), return")  
        elif self.comm == particle:
            print(f"decohere_comm - removing id:{self.comm.id}")
            self.comm = None
        else:
            print(f"decohere_comm - commID:{self.comm.id} != searchID:{particle.id}, return")
    
    # end communication qubit functions 
    
    # begin memory qubit functions

    def swapMem(self, index):
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_swap, 
                          partial(self.complete_swapMem, index))
        print(f"Queued swap id:{self.comm.id} to ind{index}")

    def complete_swapMem(self, index):
        self.mem[index] = self.comm
        self.comm = None
        
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_coh_mem, 
                          partial(self.decohere_mem, self.mem[index], index))
        print(f"Completed swap - id:{self.mem[index].id} to ind{index}")
        print(f"Queued decohere_mem - id:{self.mem[index].id}, ind{index}")
        
    def decohere_mem(self, particle, index):
        if self.mem[index] == particle:
            print(f"decohere_mem - removed id:{self.mem[index].id}, ind{index}")
            self.mem[index] = None
            if self.mem[index] is not None:
                print("error error!")
        else:
            print(f"decohere_mem - particle mismatch, ind{index}")

    # end memory qubit functions

    # begin misc functions

    def transmit(self):
        return True
    
    def receive(self):
        return (random.random() > 0.5)
    
    
    def print(self):
        if self.comm is not None:
            print(f"comm_id: {self.comm.id}")
        else:
            print("comm: None")
        print(f"memSize: {self.memSize}")
        for i in range(self.memSize):
            if self.mem[i] is not None:
                print(f"mem[{i}]_id: {self.mem[i].id}")
            else:
                print(f"mem[{i}]: None")
        print(f"genTime: {self.time_generate}")
        print(f"swapTime: {self.time_swap}")
        print(f"schedule: {self.schedule}")
        
    # end misc functions        
