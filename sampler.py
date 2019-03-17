import random
import math

class Sampler(object):
    def __init__(self, n=20, bias=50):
        self.empiricalState = []
        self.biasedSample = []
        self.unbiasedSample = []
        self.bias = bias
        self.n = n

    def recordGamestate(self, gamestate):
        self.empiricalState.append(gamestate)
        if random.uniform(0,1) <= math.exp(-(len(self.empiricalState))/self.bias):
            if len(self.biasedSample) >= self.n :
                self.biasedSample.pop(0)
            self.biasedSample.append(gamestate)
        if random.uniform(0,1) <= 1/len(self.empiricalState):
            if len(self.unbiasedSample) >= self.n :
                self.unbiasedSample.pop(0)
            self.unbiasedSample.append(gamestate)