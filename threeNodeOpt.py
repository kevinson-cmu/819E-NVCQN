import Q_cables
import Q_nodes
import Q_particles
import Q_schedule
import random
import multiprocessing
import time
from functools import partial
import matplotlib.pyplot as plt 

# Modifiers:
# Three-node network, two entanglements
# QFC time added, coherence time * 0.78
# Potential for variable distance
memSize = 10

# Main loop function, partitioned for parallelism
def loopPartition(numIterations, x):
    # local versions of global statistics
    successes = [0] * memSize
    fails = 0
    fails_ent1_decohere = 0
    fails_ent1_maxTries = 0
    fails_swap_decohere = 0
    fails_ent2_decohere = 0
    fails_ent2_maxTries = 0
    fails_fwd1_decohere = 0
    fails_localEnt_decohere = 0
    fails_fwd2_decohere = 0
    averageTime = 0
    # globalTime = 0
    fidelity = 0
    fails_fiber = 0

    # local versions of network constructs
    sched = Q_schedule.schedule()  
    particleList = []

    def checkCoherence():
        for particle in particleList:
            if not particle.coherent:
                return False
        return True
    
    def freqUp(node1, node2):
        time_freqUp = node1.time_TBQI_CRCheck + node1.time_TBQI_stabPG
        sched.passTime(time_freqUp)
        return

    def entangle1(particle1, particle2):
        # prob_success = 0.02
        # prob_success = 0.00001
        prob_success = 0.001 # from Tiancheng's results
        
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
        
        if success:
            # TODO: update based on entanglement
            particle1.entangle(particle2)
            particle2.entangle(particle1)            
            return [True, fails_ent1_decohere, fails_ent1_maxTries] 
        else:
            reason = False
            if (not particle1.coherent and not particle2.coherent):
                fails_ent1_decohere += 1
                reason = True
            elif (not particle1.coherent):
                fails_ent1_decohere += 1
                reason = True
            elif (not particle2.coherent):
                fails_ent1_decohere += 1
                reason = True
            elif (numTries >= maxTries):
                fails_ent1_maxTries += 1
                reason = True
            if (not reason):
                print("ERROR: Entangle Failed For Reasons Unknown")

        return [False, fails_ent1_decohere, fails_ent1_maxTries]

    def entangle2(particle1, particle2):
        # prob_success = 0.02
        # prob_success = 0.00001
        prob_success = 0.001 # from Tiancheng's results

        # from Realization...
        # generation rate = 2 * alpha * p_det
        # for B-C, alpha = 0.05-0.10, p_det = 4.2*10^-4, 3.0*10^-4
        # thus, prob_success ~= 0.000048
        # prob_success = 0.000054

        # output statistics
        fails_ent2_decohere = 0
        fails_ent2_maxTries = 0

        maxTries = 450
        timePerAttempt = 0.005
        
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

        if success:
            particle1.entangle(particle2)
            particle2.entangle(particle1)
            return [True, fails_ent2_decohere, fails_ent2_maxTries]
        else:
            reason = False
            if ((not particle1.coherent) and (not particle2.coherent)):
                fails_ent2_decohere += 1
                reason = True
            elif (not particle1.coherent):
                fails_ent2_decohere += 1
                reason = True
            elif (not particle2.coherent):
                fails_ent2_decohere += 1
                reason = True
            elif (numTries >= maxTries):
                fails_ent2_maxTries += 1
                reason = True
            if (not reason):
                print("ERROR: Entangle Failed For Reasons Unknown")

        return [False, fails_ent2_decohere, fails_ent2_maxTries]

    for i in range(numIterations):

        # reset network objects
        sched.wipeAll()
        particleList = []
        # sched.resetTime()
        node1 = Q_nodes.node_NV(mS=10, sch=sched)
        node2 = Q_nodes.node_NV(mS=10, sch=sched)
        node3 = Q_nodes.node_NV(mS=10, sch=sched)
        # oc1 = Q_cables.opticCable(d=x)
        oc1 = Q_cables.opticCable(dF=0.16,d=x)
        
        # set up iteration metrics
        time_iterStart = sched.getTime()

        # from Realization of a multinode quantum network (Pompili),
        # reset memory state
        sched.passTime(node1.time_init)
        
        # time to increase frequency
        freqUp(node1, node2)
        
        # coherence time modified by visiblity difference
        node1.generate_vis(0.79)
        node2.generate_vis(0.79)
        
        # check if passes fiber
        passFiber = oc1.passes_deg()
        sched.passTime(oc1.time_ms_self())
        if not passFiber:
            fails_fiber += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue

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

        # swap memory and generate C
        node3.generate()
        node1.swapMem2(0, False)
        node2.swapMem2(0, True)
        if (not node1.comm.coherent) or (not node2.comm.coherent) or (not node3.comm.coherent):
            print("Decohered during swapMem")
            fails_swap_decohere += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue

        # update comm particle for Node 2
        node2.generate()
        
        # begin second entanglement
        entangle2Results = entangle2(node2.comm, node3.comm)
        entangleSuccess = entangle2Results[0]
        fails_ent2_decohere += entangle2Results[1]
        fails_ent2_maxTries += entangle2Results[2]
        
        if (not entangleSuccess or (random.random() > 0.5)):
            fails += 1
            continue

        fide_ent2 = ((1 - node2.infide_BC_psiP) + (1 - node2.infide_BC_psiM)) / 2
        ent2 = [fide_ent2, node2.comm, node3.comm]

        # enact phase feed-forward
        sched.passTime(node1.time_feedFwrd)
        if (not node1.comm.coherent) or (not node2.comm.coherent) or (not node3.comm.coherent):
            print("Decohered during fwd1")
            fails_fwd1_decohere += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue

        # at node2, perform local entanglement
        sched.passTime(node2.time_local_entangleMeasure)
        if (not node1.comm.coherent) or (not node2.comm.coherent) or (not node3.comm.coherent):
            print("Decohered during local entanglement")
            fails_localEnt_decohere += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue

        # at node2, perform second feed-foward
        sched.passTime(node2.time_feedFwrd)
        if (not node1.comm.coherent) or (not node2.comm.coherent) or (not node3.comm.coherent):
            print("Decohered during second fwd")
            fails_fwd2_decohere += 1
            fails += 1
            averageTime += (sched.getTime() - time_iterStart)
            continue

        fide_ghz = ent1[0] * ent2[0] * node2.fide_AC_ANYBSM
        ghz1 = [fide_ghz, node2.comm, node2.mem[0]]

        # one successful entanglement. Time to try again?
        
        node3.swapMem2(0, False)
        
        sched.passTime(1) # 1ms BSM
        sched.passTime(0.1) # 100us feedforward
        node2.comm = None
        node2.mem[0] = None

        successes[1] += 1
        averageTime += (sched.getTime() - time_iterStart)
        fidelity += ghz1[0]
        
        # end of iteration loop

    # local versions of global statistics
    output = []
    output.append(successes)
    output.append(fails)
    output.append(fails_ent1_decohere)
    output.append(fails_ent1_maxTries)
    output.append(fails_swap_decohere)
    output.append(fails_ent2_decohere)
    output.append(fails_ent2_maxTries)
    output.append(fails_fwd1_decohere)
    output.append(fails_localEnt_decohere)
    output.append(fails_fwd2_decohere)
    output.append(averageTime)
    output.append(sched.getTime())
    output.append(fidelity)
    output.append(fails_fiber)
    return output
    # end of function

# main function

if __name__ == '__main__':
    
    # catch wall clock time
    startTime_main = time.time()

    # numIterations = 6000000
    # numIterations = 1200000
    # numIterations = 6000
    # numIterations = 36000
    numIterations = 72000
    progDiv = 1
    numThreads = 12

    # init multiprocessing pool 
    pool = multiprocessing.Pool() 
    pool = multiprocessing.Pool(processes=numThreads) 
        

    # graph variable values
    # x = [0.02,0.3,1,10,25,50,75,100,125,150,175,200,225,250,275,300]
    x = [0.02,0.3,1,10]
    for i in range(int(300/12.5)):
        x.append(12.5 * (i + 1))
    y = []
    print(f"x={x}")

    # loop over indep variable
    for i in range(len(x)):
        
        # log loop iteration start time
        startTime = time.time()

        # metrics (be sure to update in loop as well)
        successes = [0] * memSize
        fails = 0
        fails_ent1_decohere = 0
        fails_ent1_maxTries = 0
        fails_swap_decohere = 0
        fails_ent2_decohere = 0
        fails_ent2_maxTries = 0
        fails_fwd1_decohere = 0
        fails_localEnt_decohere = 0
        fails_fwd2_decohere = 0
        averageTime = 0
        globalTime = 0
        fidelity = 0.0
        fails_fiber = 0

        # init pool vars and run
        inputs = []
        for j in range(numThreads):
            inputs.append(x[i])
        print(f"launching pool with x={x[i]}")
        outputs = pool.map(partial(loopPartition, int(numIterations/numThreads)), inputs)

        # sum values found in outputs
        for j in range(numThreads):
            print(outputs[j])
            for k in range(memSize):
                successes[k] += outputs[j][0][k]
            fails += outputs[j][1]
            fails_ent1_decohere += outputs[j][2]
            fails_ent1_maxTries += outputs[j][3]
            fails_swap_decohere += outputs[j][4]
            fails_ent2_decohere += outputs[j][5]
            fails_ent2_maxTries += outputs[j][6]
            fails_fwd1_decohere += outputs[j][7]
            fails_localEnt_decohere += outputs[j][8]
            fails_fwd2_decohere += outputs[j][9]
            averageTime += outputs[j][10]
            globalTime += outputs[j][11]
            fidelity += outputs[j][12]
            fails_fiber += outputs[j][13]

        # determine final statistics
        averageTime = averageTime / numIterations
        print(f"Successes: {successes}")
        print(f"Fails: {fails}")
        print(f"Fails (decohered in ent1): {fails_ent1_decohere}")
        print(f"Fails (maxTries in ent1): {fails_ent1_maxTries}")
        print(f"Fails (decohered in memory swap): {fails_swap_decohere}")
        print(f"Fails (decohered in ent2): {fails_ent2_decohere}")
        print(f"Fails (maxTries in ent2): {fails_ent2_maxTries}")
        print(f"Fails (decohered in fwd1): {fails_fwd1_decohere}")
        print(f"Fails (decohered in local ent): {fails_localEnt_decohere}")
        print(f"Fails (decohered in fwd2): {fails_fwd2_decohere}")
        print(f"Average Time (ms): {averageTime}")
        print(f"Summed Global Time (ms): {globalTime}")
        if (sum(successes) == 0):
            print(f"Fidelity: N/A")
        else:    
            print(f"Fidelity: {fidelity / float(sum(successes))}")
        print(f"Fails (fiber): {fails_fiber}")
        
        print(f"Success Rate: {sum(successes) / float(numIterations)}")
        if (sum(successes) == 0):
            print(f"seconds per Successes: N/A")
        else:    
            print(f"seconds per Successes: {(globalTime / 1000.0) / sum(successes)}")
        
        print(f"Wallclock Time (s): {time.time() - startTime}")

        # PLOT: save communication rate (Hz)
        y.append(sum(successes) / (globalTime / 1000.0))

    # Final, overall statistics
    print(f"Overall Wallclock Time (s): {time.time() - startTime_main}")

    # PLOT: generate graph  
    plt.plot(x, y)
    # plt.plot(x, y, label="Plot1")
    plt.xlabel('x - Distance (km)') 
    plt.ylabel('y - Comm Rate (Hz)')  
    plt.title('Comm Rate By Distance') 
    plt.show()