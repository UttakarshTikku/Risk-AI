import pandas as pd
import numpy as np
import glob
import heapq

class Intent_Engine(object):
    def __init__(self, whoami):
        path = "./"+whoami+"_REC/*.csv"
        all_files = glob.glob(path)
        li = []
        for filename in sorted(all_files):
            df = pd.read_csv(filename, index_col=None, header=0)
            li.append(df)
        self.frame = pd.concat(li, axis=0, ignore_index=True)
        self.WINDOW_SIZE = 5

    def record_online(self, wsi):
        for row in wsi:
            data = pd.DataFrame({k:v for _,(k,v) in enumerate(row)}, index=[0])
            self.frame = self.frame.append(data)
        self.find_intent()

    def find_intent(self):
        conquer_one_territory = self.intent_conquer_one_territory()
        occupy_continent = self.intent_occupy_continent()
        fortress_continent = self.intent_fortress_continent()
        maximise_num_units_in_territory = self.intent_maximise_num_units_in_territory()
        occupy_territory_enemy_continent = self.intent_occupy_territory_enemy_continent()
        eliminate_enemy_player = self.intent_eliminate_enemy_player()

    def intent_conquer_one_territory(self):
        return True

    def intent_occupy_continent(self):
        last = self.frame.tail(self.WINDOW_SIZE)
        percentage = last.filter(regex=(".*_PERCENTAGE"))
        pc_dict = percentage.to_dict(orient='records')[1]
        temp = []
        continents = []
        for c in pc_dict.keys():
            if pc_dict[c] < 100 and pc_dict[c] > 50:
                temp.append(c.split('_')[0])
        forces = last.filter(regex=(".*_FORCES"))
        forces_dict = forces.to_dict(orient='records')
        for f in forces_dict[0].keys():
            if f.split('_')[0] in temp and not f.split('_')[1] == "BORDER":
                heapq.heappush(continents,(forces_dict[0][f] - forces_dict[1][f], f.split('_')[0]))
        return continents

    def intent_fortress_continent(self):
        last = self.frame.tail(self.WINDOW_SIZE)
        border_forces = last.filter(regex=(".*_BORDER_FORCES"))
        bf_dict = border_forces.to_dict(orient='records')
        fortress= []
        for key in bf_dict[0].keys():
            delta = bf_dict[0][key] - bf_dict[len(bf_dict) - 1][key]
            if delta < 0:
                heapq.heappush(fortress,( delta, key.split('_')[0]))
        return fortress

    def intent_maximise_num_units_in_territory(self):

        return True

    def intent_occupy_territory_enemy_continent(self):
        last = self.frame.tail(1)
            return True

    def intent_eliminate_enemy_player(self):
        return True