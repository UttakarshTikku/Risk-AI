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
import previous_turn_checker as ptc
import configuration as conf

class Recorder(object):
    def __init__(self, whoami):
        self.whoami = whoami
        self.intent = intent_engine.Intent_Engine(whoami,5,False,True)
        self.intents = []
        self.old_wsi = []
        self.predictions = []
 
    # This method is used to record the world state indicators and game state from the
    # game data. This data is then sent to the intent engine which predicts the intent
    # of the agents using the WSIs and Game States.
    # This method also saves the world state indicators from previous turn and compares
    # the change in World State Indicators with the predicted intents. By doing so, it
    # prepares the training data for the intent engine.
    # Additionally, this method writes the WSIs and related data into CSV files for
    # future use.
    def recordGamestate(self, world, game):
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
            if conf.recorder_ON:
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
        if conf.recorder_ON:
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
        previous_turn_results = ptc.find_previous_move_results(self.old_wsi, list_of_wsi, self.whoami, world)
        learner_data = []
        for i in self.intents:
            for ai in ai_names:
                if i[0] == ai[0]:
                    for ptr in previous_turn_results:
                        if ptr[0] == ai[1]:
                            learner_data.append(ptc.merge_intended_and_actual(ptr[0], i[1],ptr[1], world))
        if conf.recorder_ON:
            if len(learner_data) > 0:
                insert_header = False
                if not Path('./'+self.whoami+'_REC/learner_data.csv').exists() :
                    insert_header = True
                recorder = open('./'+self.whoami+'_REC/learner_data.csv','a')
                with recorder:
                    for i in range(0,len(learner_data)):
                        row = learner_data[i]
                        writer = csv.DictWriter(recorder,row.keys())
                        if insert_header:
                            writer.writerow({k:k for k,v in row.items()})
                            insert_header = False
                        writer.writerow(row)
        self.intents = []
        self.predictions = []
        self.intent.record_online(list_of_wsi, world_outlook)
        for ai in ai_names:
            temp = self.intent.find_intent(game, ai[1])
            self.intents.append((ai[0],temp))
            self.predictions.append((ai[0], self.intent.get_intent_predictions(ai[1], ptc.expand_intent(temp, world))))
        self.old_wsi = list_of_wsi

    # Before the recorder is torn down, we need to rename the CSV files generated during the 
    # gameplay to prevent naming clashes and clobbering of data in subsequent runs.
    def __del__(self):
        if conf.recorder_ON:
            timestamp = str(round(time.time() * 1000))
            os.rename('./'+self.whoami+'_REC/record.csv', './'+self.whoami+'_REC/record'+timestamp+'.csv')
            os.rename('./'+self.whoami+'_REC/world_outlook.csv', './'+self.whoami+'_REC/world_outlook'+timestamp+'.csv')
            os.rename('./'+self.whoami+'_REC/learner_data.csv', './'+self.whoami+'_REC/learner_data'+timestamp+'.csv')