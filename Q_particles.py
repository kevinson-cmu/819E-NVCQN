import random

class particle:

    id = 0

    def __init__(self):
        self.id = int(random.random() * 1000)
    
    def measure(self):
        return random() > 0.5