# 819E scheduler class

class schedule:

    # global time variable
    globalTime = 0
    # format: time, {function:[]}
    events = []

    def __init__(self):
        self.globalTime = 0
        self.events = []

    def getTime(self):
        return self.globalTime
    
    def add(self, time, func):
        self.events.append([time, func])

    def byTime(self, e):
        return e[0]

    def eval(self):
        self.events.sort(key=self.byTime)
        event = self.events[0]
        self.globalTime = event[0]
        func = event[1]
        self.events.remove(event)
        # print(f"Time: {self.globalTime}; Running function {func}")
        func()

    def evalAll(self):
        while len(self.events) > 0:
            self.eval()

    def passTime(self, time):
        self.events.sort(key=self.byTime)
        if len(self.events) == 0:
            return
        nextTime = self.events[0][0]
        eventHappens = (self.globalTime + time >= nextTime)
        
        while eventHappens:
            self.eval()
            self.events.sort(key=self.byTime)
            if (len(self.events) == 0):
                break
            nextTime = self.events[0][0]
            eventHappens = (self.globalTime + time > nextTime)
            
        self.globalTime += time
        # print(f"passed time {time}, globalTime: {self.globalTime}")


    def goToTime(self, time):
        self.events.sort(key=self.byTime)
        if len(self.events) == 0:
            return
        nextTime = self.events[0][0]
        eventHappens = (time >= nextTime)
        
        while eventHappens:
            self.eval()
            self.events.sort(key=self.byTime)
            if len(self.events) == 0:
                return
            nextTime = self.events[0][0]
            eventHappens = (time >= nextTime)

        # print(f"completed up to time {time}")
        self.globalTime = time
            
    def wipeAll(self):
        del self.events[:]
        self.events = []
        # print(f"wiped all events")

    def resetTime(self):
        self.globalTime = 0.0

    def reset(self):
        self.wipeAll()
        self.resetTime()
