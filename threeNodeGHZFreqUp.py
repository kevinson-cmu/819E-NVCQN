import Q_cables
import Q_nodes
import Q_particles
import Q_schedule
import random
import multiprocessing
import time

# Main loop function, partitioned for parallelism

# loop for iterations
# if the probability is bad, 
# average time should be 450 * (4ish us) -> 1.8ms?

def loopPartition(numIterations):
    # local versions of global statistics
    successes = 0
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

    # local versions of network constructs
    sched = Q_schedule.schedule()  
    particleList = []

    def entangle1(particle1, particle2):
        # prob_success = 0.02
        # prob_success = 0.00001
        
        # from Realization...
        # generation rate = 2 * alpha * p_det
        # for A-B, alpha = 0.05-0.07, p_det = 3.6*10^-4, 4.4*10^-4
        # thus, prob_success ~= 0.000048
        prob_success = 0.000048

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

    def entangle2(particle1, particle2):
        # print(f"entangle2 started at time {sched.getTime()}!")
        # prob_success = 0.02
        # prob_success = 0.00001

        # from Realization...
        # generation rate = 2 * alpha * p_det
        # for B-C, alpha = 0.05-0.10, p_det = 4.2*10^-4, 3.0*10^-4
        # thus, prob_success ~= 0.000048
        prob_success = 0.000054

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
            # TODO: update based on entanglement
            particle1.entangle(particle2)
            particle2.entangle(particle1)
            # print(f"Entanglement successful. Tries:{numTries}.")
            return [True, fails_ent2_decohere, fails_ent2_maxTries]
        else:
            reason = False
            # print("Entangle2 Failed")
            if ((not particle1.coherent) and (not particle2.coherent)):
                # print("Particle 1 & 2 decohered")
                fails_ent2_decohere += 1
                reason = True
            elif (not particle1.coherent):
                # print("Particle 1 decohered")
                fails_ent2_decohere += 1
                reason = True
            elif (not particle2.coherent):
                # print("Particle 2 decohered")
                fails_ent2_decohere += 1
                reason = True
            elif (numTries >= maxTries):
                # print("Max tries exceeded")
                fails_ent2_maxTries += 1
                reason = True
            if (not reason):
                print("ERROR: Entangle Failed For Reasons Unknown")

        return [False, fails_ent2_decohere, fails_ent2_maxTries]

    for i in range(numIterations):

        # print options
        # if (i % (numIterations / progDiv) == 0):
        #     print(f"Progress: {i / (numIterations/progDiv)}/{progDiv}")
        # print(".", end='', flush=True)

        # reset network objects
        sched.wipeAll()
        # sched.resetTime()
        node1 = Q_nodes.node_NV(mS=1, sch=sched)
        node2 = Q_nodes.node_NV(mS=1, sch=sched)
        node3 = Q_nodes.node_NV(mS=1, sch=sched)
        oc1 = Q_cables.opticCable()
        
        # set up iteration metrics
        time_iterStart = sched.getTime()

        # from Realization of a multinode quantum network (Pompili),
        # attempt entanglement between two nodes
        node1.generate()
        node2.generate()
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
        
        if (not entangleSuccess):
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

        successes += 1
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
    return output
    # end of function

# main function

if __name__ == '__main__':
    
    # catch wall clock time
    startTime = time.time()

    # metrics (be sure to update in loop as well)
    successes = 0
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

    # numIterations = 6400000
    # numIterations = 6000000
    numIterations = 6000
    progDiv = 1
    numThreads = 12

    # init and run multiprocessing pool 
    pool = multiprocessing.Pool() 
    pool = multiprocessing.Pool(processes=numThreads) 
    inputs = []
    for i in range(numThreads):
        inputs.append(int(numIterations/numThreads))
    print(inputs)
    outputs = pool.map(loopPartition, inputs)

    # sum values found in outputs
    for i in range(numThreads):
        print(outputs[i])
        successes += outputs[i][0]
        fails += outputs[i][1]
        fails_ent1_decohere += outputs[i][2]
        fails_ent1_maxTries += outputs[i][3]
        fails_swap_decohere += outputs[i][4]
        fails_ent2_decohere += outputs[i][5]
        fails_ent2_maxTries += outputs[i][6]
        fails_fwd1_decohere += outputs[i][7]
        fails_localEnt_decohere += outputs[i][8]
        fails_fwd2_decohere += outputs[i][9]
        averageTime += outputs[i][10]
        globalTime += outputs[i][11]
        fidelity += outputs[i][12]

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