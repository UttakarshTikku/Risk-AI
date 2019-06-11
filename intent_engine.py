import pandas as pd
import numpy as np
import glob
import heapq
import gc
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB

class Intent_Engine(object):
    """
    The intent engine loads the learner data from previous games and uses it to train the intent classifier.
    It uses a multi-label classifier implemented with LinearSVCs to recognise intents.
    """
    def __init__(self, whoami, window_size=2, load_previous_info=False, load_learner_data=False):
        self.whoami = whoami
        self.WINDOW_SIZE = window_size
        path = "./"+whoami+"_REC/record*.csv"
        all_files = sorted(glob.glob(path))
        if len(all_files) > 2:
            all_files = all_files[-2:]
        li = []
        if load_previous_info:
            for filename in all_files:
                df = pd.read_csv(filename, index_col=None, header=0)
                li.append(df)
        if len(li) <= 0:
            self.frame = pd.DataFrame()
        elif len(li) <= 10*self.WINDOW_SIZE:
            self.frame = pd.concat(li, axis=0, ignore_index=True, sort=False)
        else:
            self.frame = pd.concat(li, axis=0, ignore_index=True, sort=False).tail(10*self.WINDOW_SIZE)
        path = "./"+whoami+"_REC/world_outlook*.csv"
        all_files = sorted(glob.glob(path))
        li = []
        if len(all_files) > 2:
            all_files = all_files[-2:]
        if load_previous_info:
            for filename in sorted(all_files):
                df = pd.read_csv(filename, index_col=None, header=0)
                li.append(df)
        if len(li) <= 0:
            self.world_outlook = pd.DataFrame()
        elif len(li) <= 10*self.WINDOW_SIZE:
            self.world_outlook = pd.concat(li, axis=0, ignore_index=True, sort=False)
        else:
            self.world_outlook = pd.concat(li, axis=0, ignore_index=True, sort=False).tail(10*self.WINDOW_SIZE)
        gc.collect()
        path = "./"+whoami+"_REC/learner_data*.csv"
        all_files = sorted(glob.glob(path))
        li = []
        if len(all_files) > 40:
            all_files = all_files[-40:]
        if load_learner_data:
            for filename in sorted(all_files):
                df = pd.read_csv(filename, index_col=None, header=0)
                li.append(df)
        if len(li) <= 0:
            self.learner_data = pd.DataFrame()
        else:
            self.learner_data = pd.concat(li, axis=0, ignore_index=True, sort=False)
        self.ai_types = []
        if 'AI_NAME' in self.learner_data:
            self.ai_types = self.learner_data.AI_NAME.unique()
        self.classifiers = {}
        if len(self.ai_types) > 0:
            data = self.learner_data
            ai = "any"
            X = data[[
                'conquer_one_territory'
                ,'eliminate_enemy_player'
                ,'fortress_Africa'
                ,'fortress_Asia'
                ,'fortress_Australia'
                ,'fortress_Europe'
                ,'fortress_North America'
                ,'fortress_South America'
                ,'maximise_num_units_in_Africa'
                ,'maximise_num_units_in_Asia'
                ,'maximise_num_units_in_Australia'
                ,'maximise_num_units_in_Europe'
                ,'maximise_num_units_in_North America'
                ,'maximise_num_units_in_South America'
                ,'occupy_Africa'
                ,'occupy_Asia'
                ,'occupy_Australia'
                ,'occupy_Europe'
                ,'occupy_North America'
                ,'occupy_South America'
                ,'occupy_territory_enemy_continent'
            ]]
            self.classifiers[ai+"_conquer_one_territory"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['conquered_one_territory']])
            self.classifiers[ai+"_eliminate_enemy_player"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['eliminated_enemy_player']])
            self.classifiers[ai+"_fortress_Africa"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_Africa']])
            self.classifiers[ai+"_fortress_Asia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_Asia']])
            self.classifiers[ai+"_fortress_Australia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_Australia']])
            self.classifiers[ai+"_fortress_Europe"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_Europe']])
            self.classifiers[ai+"_fortress_North America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_North America']])
            self.classifiers[ai+"_fortress_South America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['fortressed_South America']])
            self.classifiers[ai+"_maximise_num_units_in_Africa"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_Africa']])
            self.classifiers[ai+"_maximise_num_units_in_Asia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_Asia']])
            self.classifiers[ai+"_maximise_num_units_in_Australia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_Australia']])
            self.classifiers[ai+"_maximise_num_units_in_Europe"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_Europe']])
            self.classifiers[ai+"_maximise_num_units_in_North America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_North America']])
            self.classifiers[ai+"_maximise_num_units_in_South America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['maximised_num_units_in_South America']])
            self.classifiers[ai+"_occupy_Africa"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_Africa']])
            self.classifiers[ai+"_occupy_Asia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_Asia']])
            self.classifiers[ai+"_occupy_Australia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_Australia']])
            self.classifiers[ai+"_occupy_Europe"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_Europe']])
            self.classifiers[ai+"_occupy_North America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_North America']])
            self.classifiers[ai+"_occupy_South America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_South America']])
            self.classifiers[ai+"_occupy_territory_Africa"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_Africa']])
            self.classifiers[ai+"_occupy_territory_Asia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_Asia']])
            self.classifiers[ai+"_occupy_territory_Australia"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_Australia']])
            self.classifiers[ai+"_occupy_territory_Europe"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_Europe']])
            self.classifiers[ai+"_occupy_territory_North America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_North America']])
            self.classifiers[ai+"_occupy_territory_South America"] =  OneVsRestClassifier(LinearSVC(C=100.)).fit(X, data[['occupied_territory_South America']])

    """
    This method is used to record the world state indicators and evolution of the game overtime,
    over a specific sized window.
    """        
    def record_online(self, wsi, world_outlook):
        for row in wsi:
            data = pd.DataFrame({k:v for _,(k,v) in enumerate(row)}, index=[0])
            self.frame = self.frame.append(data)
        self.world_outlook = self.world_outlook.append(pd.DataFrame({k:v for _,(k,v) in enumerate(row)}, index=[0]))

    """
    This method creates the intent vector at the end of it's run. It calls the various fitness 
    functions and uses the model-based AI reasoning to produce the output.
    """
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

    # This is an intent fitness function developed arbitrarily for model-based reasoning
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

    # This is an intent fitness function developed arbitrarily for model-based reasoning
    def intent_occupy_continent(self, data):
        last = data.tail(self.WINDOW_SIZE)
        percentage = last.filter(regex=(".*_PERCENTAGE"))
        pc_dict = {}
        if len(percentage.to_dict(orient='records')) > 1:
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
                heapq.heappush(continents,(forces_dict[0][f] - forces_dict[len(forces_dict) - 1][f], f.split('_')[0]))
        return continents

    # This is an intent fitness function developed arbitrarily for model-based reasoning
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

    # This is an intent fitness function developed arbitrarily for model-based reasoning
    def intent_maximise_num_units_in_territory(self, game):
        candidates = []
        window = self.world_outlook.tail(round(self.WINDOW_SIZE/2))
        list_territories = sorted([x[0] for x in game.world.territories.items()])
        for territory in list_territories:
            territory_outlook = window.filter(regex=(territory+"_.*"))
            if not territory+"_OCCUPANT" in territory_outlook.index and not territory+"_FORCES" in territory_outlook.index:
                continue
            if len(territory_outlook[territory+"_OCCUPANT"].unique().tolist()) == 1:
                if len(territory_outlook[territory+"_FORCES"].unique().tolist()) < round(self.WINDOW_SIZE/2):
                    continue
                candidates.append(territory)
        return candidates

    # This is an intent fitness function developed arbitrarily for model-based reasoning
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

    # This is an intent fitness function developed arbitrarily for model-based reasoning
    def intent_eliminate_enemy_player(self, game):
        candidates = []
        for p in game.players:
            if game.players[p].territory_count > 0 and game.players[p].territory_count < 4:
                candidates.append(p)
        return candidates

    # This method merges the model based reasoning with data-driven learning to generate
    # a hybrid reasoning for the AI agent.
    def get_intent_predictions(self, ai_name, expanded_intent):
        prediction_dict = {}
        temp = np.fromiter(expanded_intent.values(), dtype=np.int).reshape(1,-1)
        for key in self.classifiers:
            if True or ai_name in key:
                prediction_dict[key] = self.classifiers[key].predict(temp)
        return prediction_dict