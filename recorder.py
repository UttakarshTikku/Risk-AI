import json
import math
import random
import csv
import pandas as pd
from pathlib import Path
import os
import collections

import time
import intent_engine

class Recorder(object):
    def __init__(self, whoami):
        self.whoami = whoami
        self.intent = intent_engine.Intent_Engine(whoami,5,True)
        self.learner = intent_engine.Intent_Engine(whoami)
        self.intents = []

    def recordGamestate(self, world, game):
        self.intents = []
        list_of_wsi = []
        world_outlook = set()
        ai_names = []
        for p in game.players:
            list_for_opponent = []
            ai_name = game.players[p].ai.__str__().split()[0].split('.')
            ai_name = ai_name[len(ai_name) - 1]
            ai_names.append((game.players[p].name, ai_name))
            list_for_opponent.append(("AI_NAME",ai_name))
            list_for_opponent.append(("FORCES", game.players[p].forces))
            list_for_opponent.append(("TERRITORIES", len(list(game.players[p].territories)) ))
            max_forces_territory = ("",0)
            continents_fully_owned = 0
            for a in world.areas.values():
                area_forces = 0
                area_border_forces = 0
                list_for_opponent.append((a.name+"_TERRITORIES",len(set(a.territories).intersection(game.players[p].territories))))
                if len(a.territories) == len(set(a.territories).intersection(game.players[p].territories)):
                    continents_fully_owned += 1
                list_for_opponent.append((a.name+"_PERCENTAGE",100 * len(set(a.territories).intersection(game.players[p].territories))/len(set(a.territories))))
                for t in a.territories:
                    world_outlook.add((t.name+"_OCCUPANT", "UNOCCUPIED" if t.owner==None else t.owner.name))
                    world_outlook.add((t.name+"_FORCES", t.forces))
                    if t.owner != None: 
                        if t.owner.name == p :
                            if max_forces_territory[1] < t.forces:
                                max_forces_territory = (t.name, t.forces)
                            area_forces += t.forces
                            if t.area_border:
                                area_border_forces += t.forces
                list_for_opponent.append((a.name+"_FORCES", area_forces))
                list_for_opponent.append((a.name+"_BORDER_FORCES", area_border_forces))
            list_for_opponent.append(("CONTINENTS_FULLY_OWNED", continents_fully_owned))
            list_of_wsi.append(list_for_opponent)
            insert_header = False
            if not Path('./'+self.whoami+'_REC/record.csv').exists() :
                insert_header = True
            recorder = open('./'+self.whoami+'_REC/record.csv','a')
            with recorder:
                row = dict(list_for_opponent)
                od=collections.OrderedDict(sorted(row.items()))
                writer = csv.DictWriter(recorder,od.keys())
                if insert_header:
                    writer.writerow({k:k for k,v in od.items()})
                writer.writerow(od)
        insert_header = False
        if not Path('./'+self.whoami+'_REC/world_outlook.csv').exists() :
            insert_header = True
        recorder = open('./'+self.whoami+'_REC/world_outlook.csv','a')
        with recorder:
            row = dict(world_outlook)
            od=collections.OrderedDict(sorted(row.items()))
            writer = csv.DictWriter(recorder,od.keys())
            if insert_header:
                writer.writerow({k:k for k,v in od.items()})
            writer.writerow(od)
        self.intent.record_online(list_of_wsi, world_outlook)
        for ai in ai_names:
            self.intents.append((ai[0],self.intent.find_intent(game, ai[1])))

    def __del__(self):
        timestamp = str(round(time.time() * 1000))
        os.rename('./'+self.whoami+'_REC/record.csv', './'+self.whoami+'_REC/record'+timestamp+'.csv')
        os.rename('./'+self.whoami+'_REC/world_outlook.csv', './'+self.whoami+'_REC/world_outlook'+timestamp+'.csv')