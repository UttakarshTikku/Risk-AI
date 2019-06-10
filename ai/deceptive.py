from ai import AI
import random
import collections
import math
from recorder import Recorder
from decision_engine import Decision_Engine
import configuration as conf

class DeceptiveAI(AI):
    """
    BetterAI: Thinks about what it is doing a little more - picks a priority
    continent and priorities holding and reinforcing it.
    """
    
    def __init__(self, player, game, world, **kwargs):
        deception_strategy = 0
        for name, strategy in conf.deception_modes:
            if player.name == name:
                deception_strategy = strategy
        self.recorder = Recorder("Deceptive"+str(deception_strategy)+"AI")
        self.decision_engine = Decision_Engine(5, world, True,deception_strategy)
        super(DeceptiveAI, self).__init__( player, game, world, **kwargs)
    
    def start(self):
        self.saveGamestate()
        self.area_priority = self.decision_engine.area_priority_gen(self.world, self.player)

    def priority(self):
        return self.decision_engine.priority(self.world, self.player)

    def initial_placement(self, empty, available):
        self.saveGamestate()
        if empty:
            for x,y,z in self.decision_engine.area_centrality:
                for t in z:
                    for t_1 in empty:
                        if t_1.name == t[1]:
                            return t_1
        else:
            return random.choice(self.priority())

    def saveGamestate(self):
        self.recorder.recordGamestate(self.world, self.game)

    def reinforce(self, available):
        self.saveGamestate()
        return self.decision_engine.reinforce(available, self.world, self.player, self.recorder.intents, self.recorder.predictions)

    def attack(self):
        self.saveGamestate()
        return self.decision_engine.attack(self.world, self.player, self.recorder.intents, self.recorder.predictions)
    
    def freemove(self):
        self.saveGamestate()
        return self.decision_engine.freemove(self.world, self.player, self.recorder.intents, self.recorder.predictions)