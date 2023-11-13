import Q_nodes
import Q_particles
import Q_schedule

# optical cable modeling
class opticCable:
    # 1.0 = no degradation
    degradationFactor = 1.0 
    distance = 1.0

    def __init__(self, dF=1.0, d=1.0):
        self.degradationFactor = dF
        self.distance = d

    def comm(self, send, receive):
        return (send and receive)

# declare schedule
sched = Q_schedule.schedule()  


# instantiate network
node1 = Q_nodes.node_NV(sch=sched)
# node1.generate()
# node1.print()

node2 = Q_nodes.node_NV(mS=10, sch=sched)
node2.generate()
# node2.print()
node2.swapMem(0)
sched.evalAll()
node2.print()

oc1 = opticCable()



# begin network traffic simulation

# transmit a signal
successes = 0
fails = 0
for i in range(100):
    result = oc1.comm(node1.transmit(), node2.receive())

    if (result):
        # print("got it")
        successes += 1
    else:
        # print("not got")
        fails += 1

print(f"Successes: {successes}")
print(f"Fails: {fails}")

