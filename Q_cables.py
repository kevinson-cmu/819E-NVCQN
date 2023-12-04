import random
import math

# optical cable modeling

class opticCable:
    
    # in the 1.5um WL range, loss is 0.2 dB/km
    degradationFactor = 0.2 
    
    # for use if distance doesn't change
    distance = 1.0

    SoL = 300000.0 # speed of light: km/s

    def __init__(self, dF=0.2, d=1.0):
        self.degradationFactor = dF
        self.distance = d

    def comm(self, send, receive):
        passesDegradation = (random.random() <= self.degradationFactor)
        return (send and receive) and passesDegradation
    
    def passes_deg(self):    
        return (random.random() <= self.loss_lin(self.distance)) 
    
    def loss_lin(self, distance):
        linScale = 10 ** ((self.degradationFactor * distance) / 10)
        return 1.0 / linScale
    
    def time_seconds(self, distance):
        return distance / self.SoL

    def time_ms(self, distance):
        return (distance / self.SoL) / 1000.0
    
    def time_ms_self(self):
        return (self.distance / self.SoL) / 1000.0