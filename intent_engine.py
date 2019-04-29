import pandas as pd
import numpy as np
import glob
import heapq

class Intent_Engine(object):
    def __init__(self, whoami, window_size=2, load_previous_info=False):
        self.whoami = whoami
        path = "./"+whoami+"_REC/record*.csv"
        all_files = glob.glob(path)
        li = []
        if load_previous_info:
            for filename in sorted(all_files):
                df = pd.read_csv(filename, index_col=None, header=0)
                li.append(df)
        if len(li) <= 0:
            self.frame = pd.DataFrame()
        else:
            self.frame = pd.concat(li, axis=0, ignore_index=True, sort=False)
        self.WINDOW_SIZE = window_size
        path = "./"+whoami+"_REC/world_outlook*.csv"
        all_files = glob.glob(path)
        li = []
        if load_previous_info:
            for filename in sorted(all_files):
                df = pd.read_csv(filename, index_col=None, header=0)
                li.append(df)
        if len(li) <= 0:
            self.world_outlook = pd.DataFrame()
        else:
            self.world_outlook = pd.concat(li, axis=0, ignore_index=True, sort=False)

    def record_online(self, wsi, world_outlook):
        for row in wsi:
            data = pd.DataFrame({k:v for _,(k,v) in enumerate(row)}, index=[0])
            self.frame = self.frame.append(data)
        self.world_outlook = self.world_outlook.append(pd.DataFrame({k:v for _,(k,v) in enumerate(row)}, index=[0]))

    def find_intent(self, game, player):
        data = self.frame.loc[self.frame['AI_NAME'] == player]
        conquer_one_territory = self.intent_conquer_one_territory(data)
        occupy_continent = self.intent_occupy_continent(data)
        fortress_continent = self.intent_fortress_continent(data)
        maximise_num_units_in_territory = self.intent_maximise_num_units_in_territory(game)
        occupy_territory_enemy_continent = self.intent_occupy_territory_enemy_continent(data)
        eliminate_enemy_player = self.intent_eliminate_enemy_player(game)
        intent_dict = {
                        "conquer_one_territory": conquer_one_territory \
                        ,"occupy_continent":occupy_continent \
                        ,"fortress_continent":fortress_continent \
                        ,"maximise_num_units_in_territory":maximise_num_units_in_territory \
                        ,"occupy_territory_enemy_continent":occupy_territory_enemy_continent \
                        ,"eliminate_enemy_player":eliminate_enemy_player \
        }
        return intent_dict

    def intent_conquer_one_territory(self, data):
        confidence = 0
        window = data.tail(self.WINDOW_SIZE)
        percentage = window.filter(regex=(".*_PERCENTAGE"))
        pc_dict = percentage.to_dict(orient='records')
        keys = pc_dict[0].keys()
        for i in range(0, len(pc_dict)-1 ):
            for key in keys:
                if pc_dict[i][key] < 50:
                    confidence += 1
        return confidence / self.WINDOW_SIZE

    def intent_occupy_continent(self, data):
        last = data.tail(self.WINDOW_SIZE)
        percentage = last.filter(regex=(".*_PERCENTAGE"))
        pc_dict = percentage.to_dict(orient='records')[1]
        temp = []
        continents = []
        for c in pc_dict.keys():
            if pc_dict[c] > 50:
                temp.append(c.split('_')[0])
        forces = last.filter(regex=(".*_FORCES"))
        forces_dict = forces.to_dict(orient='records')
        for f in forces_dict[0].keys():
            if f.split('_')[0] in temp and not f.split('_')[1] == "BORDER":
                heapq.heappush(continents,(forces_dict[0][f] - forces_dict[1][f], f.split('_')[0]))
        return continents

    def intent_fortress_continent(self, data):
        last = data.tail(self.WINDOW_SIZE)
        border_forces = last.filter(regex=(".*_BORDER_FORCES"))
        bf_dict = border_forces.to_dict(orient='records')
        fortress= []
        for key in bf_dict[0].keys():
            delta = bf_dict[0][key] - bf_dict[len(bf_dict) - 1][key]
            if delta < 0:
                heapq.heappush(fortress,( delta, key.split('_')[0]))
        return fortress

    def intent_maximise_num_units_in_territory(self, game):
        candidates = []
        window = self.world_outlook.tail(round(self.WINDOW_SIZE/2))
        list_territories = sorted([x[0] for x in game.world.territories.items()])
        for territory in list_territories:
            territory_outlook = window.filter(regex=(territory+"_.*"))
            if len(territory_outlook[territory+"_OCCUPANT"].unique().tolist()) == 1:
                if len(territory_outlook[territory+"_FORCES"].unique().tolist()) < round(self.WINDOW_SIZE/2):
                    continue
                candidates.append(territory)
        return candidates

    def intent_occupy_territory_enemy_continent(self, data):
        window = data.tail(self.WINDOW_SIZE)
        last = window.tail(1)
        percentage = last.filter(regex=(".*_PERCENTAGE"))
        pc_dict = percentage.to_dict(orient='records')[0]
        confidence = 0
        for c in pc_dict.keys():
            if pc_dict[c] == 100 or pc_dict[c] < 50:
                confidence += 1
        percentage = window.filter(regex=(".*_PERCENTAGE"))
        pc_dict = percentage.to_dict(orient='records')
        keys = pc_dict[0].keys()
        for i in range(0, len(pc_dict)-2 ):
            for key in keys:
                if pc_dict[i+1][key] <= pc_dict[i][key]:
                    confidence += 1
        return confidence/self.WINDOW_SIZE

    def intent_eliminate_enemy_player(self, game):
        candidates = []
        for p in game.players:
            if game.players[p].territory_count > 0 and game.players[p].territory_count < 4:
                candidates.append(p)
        return candidates