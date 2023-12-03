import Q_cables
import Q_nodes
import Q_particles
import Q_schedule
import random
import multiprocessing
import time
from functools import partial
import matplotlib.pyplot as plt 


# Main loop function, partitioned for parallelism

# loop for iterations
# if the probability is bad, 
# average time should be 450 * (4ish us) -> 1.8ms?

def loopPartition(numIterations, x):
    # local versions of global statistics
    successes = 0
    fails = 0
    fails_fiber = 0
    fails_ent1_decohere = 0
    fails_ent1_maxTries = 0
    averageTime = 0
    # globalTime = 0
    fidelity = 0

    # local versions of network constructs
    sched = Q_schedule.schedule()  
    particleList = []

    def freqUp(node1, node2):
        time_freqUp = node1.time_TBQI_CRCheck + node1.time_TBQI_stabPG
        sched.passTime(time_freqUp)
        return

    def entangle1(particle1, particle2):
        # prob_success = 0.02
        prob_success = 0.000009
        
        # from Realization...
        # generation rate = 2 * alpha * p_det
        # for A-B, alpha = 0.05-0.07, p_det = 3.6*10^-4, 4.4*10^-4
        # thus, prob_success ~= 0.000048
        # prob_success = 0.000048

        # output statistics
        fails_ent1_decohere = 0
        fails_ent1_maxTries = 0
        
        maxTries = 450
        timePerAttempt = 0.0038
        
        success = False
        numTries = 0

        loopCond = particle1.coherent and particle2.coherent and (not success) \
            and (numTries < maxTries)
        
        while (loopCond):
            randVal = random.random()
            if randVal < prob_success:
                success = True
            numTries += 1

            # pass time
            sched.passTime(timePerAttempt)

            # update loop condition
            loopCond = particle1.coherent and particle2.coherent and (not success)\
                and (numTries < maxTries)
            
            # end of while loop

        # print(f"entangle1 ended at time {sched.getTime()}!")
        if success:
            # TODO: update based on entanglement
            particle1.entangle(particle2)
            particle2.entangle(particle1)
            # print(f"Entanglement successful. Tries:{numTries}.")
            return [True, fails_ent1_decohere, fails_ent1_maxTries] 
        else:
            reason = False
            # print("Entangle1 Failed")
            if (not particle1.coherent and not particle2.coherent):
                # print("Particle 1 & 2 decohered")
                fails_ent1_decohere += 1
                reason = True
            elif (not particle1.coherent):
                # print("Particle 1 decohered")
                fails_ent1_decohere += 1
                reason = True
            elif (not particle2.coherent):
                # print("Particle 2 decohered")
                fails_ent1_decohere += 1
                reason = True
            elif (numTries >= maxTries):
                # print("Max tries exceeded")
                fails_ent1_maxTries += 1
                reason = True
            if (not reason):
                print("ERROR: Entangle Failed For Reasons Unknown")

        return [False, fails_ent1_decohere, fails_ent1_maxTries]

    for i in range(numIterations):

        # reset network objects
        sched.wipeAll()
        node1 = Q_nodes.node_NV(mS=1, sch=sched)
        node2 = Q_nodes.node_NV(mS=1, sch=sched)
        node3 = Q_nodes.node_NV(mS=1, sch=sched)
        oc1 = Q_cables.opticCable(d=x) # one km fiber
        
        # set up iteration metrics
        time_iterStart = sched.getTime()

        # from Realization of a multinode quantum network (Pompili),
        # attempt entanglement between two nodes
        node1.generate()
        node2.generate()

        # check if passes fiber
        freqUp(node1, node2)
        passFiber = oc1.passes_deg()
        if not passFiber:
            fails_fiber += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue
        sched.passTime(oc1.time_ms_self())
        
        # attempt entanglement
        entangle1Results = entangle1(node1.comm, node2.comm)
        entangleSuccess = entangle1Results[0]
        fails_ent1_decohere += entangle1Results[1]
        fails_ent1_maxTries += entangle1Results[2]

        if (not entangleSuccess):
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue
        
        fide_ent1 = ((1 - node2.infide_AB_psiP) + (1 - node2.infide_AB_psiM)) / 2
        ent1 = [fide_ent1, node1.comm, node2.comm]

        # report success
        successes += 1
        averageTime += (sched.getTime() - time_iterStart)
        fidelity += ent1[0]
        
        
        # end of iteration loop

    # local versions of global statistics
    output = []
    output.append(successes)
    output.append(fails)
    output.append(fails_fiber)
    output.append(fails_ent1_decohere)
    output.append(fails_ent1_maxTries)
    output.append(averageTime)
    output.append(sched.getTime())
    output.append(fidelity)
    return output
    # end of function

# main function

if __name__ == '__main__':
    
    # catch wall clock time
    startTime_main = time.time()

    # numIterations = 6000000
    numIterations = 6000000
    # numIterations = 6000
    progDiv = 1
    numThreads = 12

    # graph variable values
    x = [100,125,150,175,200,225,250]
    y = []

    # loop over indep variable
    for i in range(len(x)):   

        startTime = time.time()

        # metrics (be sure to update in loop as well)
        successes = 0
        fails = 0
        fails_fiber = 0
        fails_ent1_decohere = 0
        fails_ent1_maxTries = 0
        averageTime = 0
        globalTime = 0
        fidelity = 0.0 

        # init and run multiprocessing pool 
        pool = multiprocessing.Pool() 
        pool = multiprocessing.Pool(processes=numThreads) 
        inputs = []
        for j in range(numThreads):
            # inputs.append(int(numIterations/numThreads))
            inputs.append(x[i])
        # print(inputs)
        # outputs = pool.map(loopPartition, inputs)
        print(f"launching pool with x={x[i]}")
        outputs = pool.map(partial(loopPartition, int(numIterations/numThreads)), inputs)

        # sum values found in outputs
        for i in range(numThreads):
            print(outputs[i])
            successes += outputs[i][0]
            fails += outputs[i][1]
            fails_fiber += outputs[i][2]
            fails_ent1_decohere += outputs[i][3]
            fails_ent1_maxTries += outputs[i][4]
            averageTime += outputs[i][5]
            globalTime += outputs[i][6]
            fidelity += outputs[i][7]

        # determine final statistics
        averageTime = averageTime / numIterations
        print(f"Successes: {successes}")
        print(f"Fails: {fails}")
        print(f"Fails (blocked in fiber): {fails_fiber}")
        print(f"Fails (decohered in ent1): {fails_ent1_decohere}")
        print(f"Fails (maxTries in ent1): {fails_ent1_maxTries}")
        print(f"Average Time (ms): {averageTime}")
        print(f"Summed Global Time (ms): {globalTime}")
        if (successes == 0):
            print(f"Fidelity: N/A")
        else:    
            print(f"Fidelity: {fidelity / float(successes)}")
        
        print(f"Success Rate: {successes / float(numIterations)}")
        if (successes == 0):
            print(f"seconds per Successes: N/A")
        else:    
            print(f"seconds per Successes: {(globalTime / 1000.0) / successes}")
        
        print(f"Wallclock Time (s): {time.time() - startTime}")
        
        # PLOT: save communication rate (Hz)
        y.append(successes / (globalTime / 1000.0))

    # Final, overall statistics
    print(f"Overall Wallclock Time (s): {time.time() - startTime_main}")

    # PLOT: generate graph  
    plt.plot(x, y)
    plt.xlabel('x - Distance (km)') 
    plt.ylabel('y - Comm Rate (Hz)')  
    plt.title('Comm Rate By Distance') 
    plt.show()