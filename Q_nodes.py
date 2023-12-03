import Q_particles
import Q_schedule
from functools import partial
import random

class node_NV:
    
    # comm: communication qubit, the N^14
    comm = None
    # mem: memory qubits, C^13 atoms surrounding NV center
    memSize = 1
    mem = [None]
    
    # while time units can be anything (as long as it is used consistently)
    # let's say time units are milliseconds
    
    # from 10 qubit memory - N^14 coherence time is around 2.3s
    # time_coh_comm = 2300.0
    # from Realization of a multinode quantum network, 11.6ms?
    time_coh_comm = 11.6

    # from 10 qubit memory - best time is 63s using dynamic decoupling + RF pulses + 
    # average times range from 4s to 25s, worse due to distance from core -> spin coupling to environment
    # time_coh_mem = 25000.0000
    # from Realization of a multinode quantum network, 11.6ms
    time_coh_mem = 11.60
    
    time_generate = 1.0

    # from Realization of a multinode quantum network
    # swap time is around 600us
    time_swap = 0.60

    # from Realization of a multinode quantum network
    # first link time is btwn .25ms - 16ms
    # second link time is btwn .7ms - 3ms?
    time_entangle_min = 0.25
    time_entangle_max = 16.0
    
    # from Realization of a multinode quantum network
    time_attempt_entangle1 = 0.0038 # 3.8us for A-B
    time_attempt_entangle2 = 0.005 # 5us for B-C
    time_local_entangleMeasure = 0.400 # 400us
    time_BSM = 1.0 # 1ms for Bell-State measurement
    time_feedFwrd = 0.100 # 100us
    time_reset = 0.600 # ~600us
    
    infide_AB_psiP = 0.180
    infide_AB_psiM = 0.189
    infide_BC_psiP = 0.192
    infide_BC_psiM = 0.189
    infide_AC_00BSM = (1-0.082)*(1-0.028)*(1-0.037)*(1-0.016)*(1-0.013)
    fide_AC_ANYBSM = (1-0.082)*(1-0.028)*(1-0.037)*(1-0.016)*(1-0.075)
    infide_AC_phi_00BSM = 0.413
    infide_AC_phi_ANYBSM = 0.449

    # from TelecomBandQInterference
    time_TBQI_CRCheck = 1.5 # 1.5ms 
    time_TBQI_stabPG = 0.2 # 200us for other stages, (the 39 photon gens each are 3.85us)  

    temperature = 1.0
    schedule = None

    def __init__(self, mS = 1, gT = 1.0, sT = 0.6, sch=None):
        self.comm = None
        self.memSize = mS
        self.mem = []
        for i in range(mS):
            self.mem.append(None)
        
        # set times
        self.time_generate = gT
        self.time_swap = sT

        self.schedule = sch

    # comm qubit functions

    def generate(self):
        if self.comm is not None:
            del self.comm
        self.comm = Q_particles.particle(self.schedule)
        
        # add "decohere particle" to scheduler
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_coh_comm, 
                          partial(self.comm.decohere))
        # print(f"Queued decohere_comm - id:{self.comm.id}. time:{globalTime + self.time_coh_comm}")
        return self.comm.id
    
    def get_comm(self):
        return self.comm
    
    def receive_comm(self, particle):
        if particle is not None:
            self.comm = particle
            # print(f"set_comm: particle received, id:{self.comm.id}")
        else:
            # print("set_comm: particle received was None, failed")
            return
    
    def rm_comm(self):
        self.comm = None
    
    # end communication qubit functions 
    
    # begin memory qubit functions

    def queue_swapMem(self, index, timeOffset):
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + timeOffset, 
                          partial(self.swapMem, index))
        # print(f"Queued swapMem to time {globalTime + timeOffset}, ind{index}")

    def swapMem(self, index, complete):
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_swap, 
                          partial(self.complete_swapMem, index))
        # print(f"Queued complete_swapMem, id:{self.comm.id} to ind{index}")
        if complete:
            self.schedule.goToTime(globalTime + self.time_swap)

    def complete_swapMem(self, index):
        # double check that qubits are actually found
        if (self.comm is not None):
            self.mem[index] = self.comm
            self.comm = None
        else:
            # print("complete_swapMem: comm qubit missing, failed")
            return
        
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_coh_mem, 
                          partial(self.decohere_mem, self.mem[index], index))
        # print(f"Completed swap - id:{self.mem[index].id} to ind{index}")
        # print(f"Queued decohere_mem - id:{self.mem[index].id}, ind{index}")
        return

    def swapMem2(self, index, complete):
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_swap, 
                          partial(self.complete_swapMem2, index))
        # print(f"Queued complete_swapMem, id:{self.comm.id} to ind{index}")
        if complete:
            self.schedule.goToTime(globalTime + self.time_swap)

    def complete_swapMem2(self, index):
        # double check that qubits are actually found
        if (self.comm is not None):
            self.mem[index] = self.comm
        else:
            # print("complete_swapMem: comm qubit missing, failed")
            return
        
        globalTime = self.schedule.getTime()
        self.schedule.add(globalTime + self.time_coh_mem, 
                          partial(self.decohere_mem, self.mem[index], index))
        # print(f"Completed swap - id:{self.mem[index].id} to ind{index}")
        # print(f"Queued decohere_mem - id:{self.mem[index].id}, ind{index}")
        return

    def decohere_mem(self, particle, index):
        if self.mem[index] == particle:
            # print(f"decohere_mem - removed id:{self.mem[index].id}, ind{index}")
            self.mem[index] = None
            if self.mem[index] is not None:
                # print("error error!")
                None
        else:
            # print(f"decohere_mem - particle mismatch, ind{index}")
            None

    # end memory qubit functions

    # begin misc functions

    def transmit(self):
        return True
    
    def receive(self):
        return True
    
    def get_time_generate(self):
        return self.time_generate
    
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
