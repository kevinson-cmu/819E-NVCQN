import random
from functools import partial

# possible bases:
# cross
# x
# possible polarizations:
# 0, 45, 90, 135

class particle:

    id = 0
    sched = None
    # wavelength?
    # one millisecond
    time_measure = 1.0 
    entangledWith = []
    polarization = None

    coherent = False
    measured = None

    def __init__(self, sch):
        self.id = int(random.random() * 1000)
        self.sched = sch
        self.coherent = True
    
    def decohere(self):
        self.coherent = False
        # print(f"particle {self} decohered; id:{self.id}, time:{self.sched.getTime()}")

    def entangle(self, particle):
        self.entangledWith.append(particle)

    def isEntangledWith(self, particle):
        return particle in self.entangledWith

    def measure(self, base):
        # add measurement to scheduler
        globalTime = self.schedule.getTime()
        self.sched.add(globalTime + self.time_measure, 
                          partial(self.complete_measure, base))
        print(f"Queued complete_measure - base:{base}")

    def complete_measure(self, base):
        result = random.random() > 0.5
        if result:
            self.measured = "UP"

        return 
    
    def __del__(self):
        self.sched = None
        # for particle in self.entangledWith:
        #     particle.entangledWith.remove(self)
        self.entangledWith = None