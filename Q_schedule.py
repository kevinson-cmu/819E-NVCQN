# 819E

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
        print(f"Time: {self.globalTime}; Running function")
        func()

    def evalAll(self):
        while len(self.events) > 0:
            self.eval()

    def passTime(self, time):
        self.events.sort(key=self.byTime)
        nextTime = self.events[0][0]
        eventHappens = (self.globalTime + time > nextTime)
        
        while eventHappens:
            eval()
            self.events.sort(key=self.byTime)
            nextTime = self.events[0][0]
            eventHappens = (self.globalTime + time > nextTime)

        print(f"passed to time {time}")
            
            
