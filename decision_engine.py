import collections
import random
import heapq
from operator import attrgetter
import networkx as nx

class Decision_Engine(object):
    def __init__(self, steps, world):
        self.steps_to_check = steps
        self.world = world
        self.continents_priority = []
        self.eliminate_territories = []
        self.territories_reinforce = []
        self.territories_attack = []
        self.enemies_eliminate = []
        self.vulnerable = []
        self.crucial = []
        self.crucial_attack = []
        self.areas_under_threat = []
        self.areas_opportunity = []
        self.perceived_threat = []
        self.create_stronghold = []
        self.most_viable_attacks = []
        self.annex_territory = []
        self.is_threatened = False
        self.G=nx.Graph()
        weighted_G=nx.Graph()
        for a in world.areas:
            for t in world.areas[a].territories:
                for adj in t.adjacent():
                    self.G.add_edge(t.name, adj.name)
        self.area_centrality = []
        self.key_value = nx.degree_centrality(self.G)
        for a in world.areas:
            count = 0
            l = []
            for t in world.areas[a].territories:
                count += self.key_value[t.name]
                l.append((self.key_value[t.name], t.name))
                for adj in t.adjacent():
                    weight = self.key_value[t.name] + self.key_value[adj.name]
                    weighted_G.add_edge(t.name, adj.name, weight=weight)
            l = sorted(l, key=lambda x: x[0])
            self.area_centrality.append((count, a,l))
        self.area_centrality = sorted(self.area_centrality, key=lambda x: x[0])
        self.G = weighted_G
        self.mst = nx.algorithms.tree.minimum_spanning_tree(self.G)

    def area_priority_gen(self, world, player):
        self.crucial = []
        territory_graph= nx.Graph()
        for t in player.territories:
            for adj in t.adjacent():
                if adj.owner.name == t.owner.name:
                    territory_graph.add_edge(t.name, adj.name)
        graphs=list(nx.connected_component_subgraphs(territory_graph))
        territories = []
        area_centrality = []
        key_value=[]
        self.G=nx.Graph()
        weighted_G=nx.Graph()
        for y in graphs:
            territories.append(y.nodes)
        for a in world.areas:
            for t in world.areas[a].territories:
                source = t.name
                for i in range(0, len(territories)):
                    if t.name in territories[i]:
                        source = "Territory"+str(i)
                for adj in t.adjacent():
                    dest = adj.name
                    for i in range(0, len(territories)):
                        if adj.name in territories[i]:
                            dest = "Territory"+str(i)
                    self.G.add_edge(source, dest)
        for i in range(0, len(territories)):
            for j in range(i + 1, len(territories)):
                if not i == j:
                    self.crucial.append(nx.shortest_path(self.G, "Territory"+str(i), "Territory"+str(j)))
        temp = []
        for c in self.crucial:
            for t in c:
                if "Territory" not in t:
                    temp.append(t)
        self.crucial = list(set(temp))
        if len(self.G) > 1:
            key_value=nx.degree_centrality(self.G)
        for a in world.areas:
            count = -99999
            l = []
            for t in world.areas[a].territories:
                if t in player.territories:
                    continue
                if count == -99999:
                    count = 0
                count += key_value[t.name]
                l.append((key_value[t.name], t.name))
                for adj in t.adjacent():
                    if adj in player.territories:
                        continue
                    weight = key_value[t.name] + key_value[adj.name]
                    weighted_G.add_edge(t.name, adj.name, weight=weight)
            l = sorted(l, key=lambda x: x[0])
            area_centrality.append((-count, a, l))
        area_centrality = sorted(area_centrality, key=lambda x: x[0])
        return [y for x,y,z in area_centrality]

    def priority(self, world, player):
        self.area_priority = self.area_priority_gen(world, player)
        priority = sorted([t for t in player.territories if t.border], 
                          key=lambda x: self.area_priority.index(x.area.name))
        priority = [t for t in priority if t.area == priority[0].area]
        return priority if priority else list(player.territories)

    def reinforce(self, available, world, player, intents):
        self.analyse_intents(intents, player)
        result = collections.defaultdict(int)
        if self.is_threatened:
            min_centrality = 99999
            territory_to_reinforce = None
            for t in player.territories:
                if self.key_value[t.name] < min_centrality:
                    min_centrality = self.key_value[t.name]
                    territory_to_reinforce = t
            result[territory_to_reinforce] += available
            return result
        for t in self.vulnerable:
            if not available > 0:
                break
            else:
                for adj in t.adjacent():
                    if t in result:
                        break
                    if not t.owner.name == adj.owner.name:
                        temp = available
                        for i in range(1,temp):
                            if self.check_recursive(t.forces + i, adj.forces, 1) > 0.5 or i == temp:
                                result[t] += i
                                available = available - i
                                break
        for t in self.perceived_threat:
            if not available > 0:
                break
            else:
                for adj in t.adjacent():
                    if t in result:
                        break
                    if not t.owner.name == adj.owner.name:
                        temp = available
                        for i in range(1,temp):
                            if self.check_recursive(t.forces + i, adj.forces, 1) > 0.5 or i == temp:
                                result[t] += i
                                available = available - i
                                break
        for t in self.territories_reinforce:
            if not available > 0:
                break
            else:
                for adj in t.adjacent():
                    if t in result:
                        break
                    if not t.owner.name == adj.owner.name:
                        temp = available
                        for i in range(1,temp):
                            if self.check_recursive(t.forces + i, adj.forces, 1) > 0.5 or i == temp:
                                result[t] += i
                                available = available - i
                                break    
        len_reinforcement_reqd = len(self.territories_reinforce)
        priority = self.priority(world, player)
        while available:     
            if len_reinforcement_reqd > 0 and random.uniform(0,1) < 0.5:
                t = random.choice(list(self.territories_reinforce))
                result[t] += 1
            else:
                result[random.choice(priority)] += 1
            available -= 1
        return result

    def attack(self, player, intents):
        self.analyse_intents(intents, player)
        if self.is_threatened:
            if len(self.most_viable_attacks) > 0:
                for t in player.territories:
                    if t.forces > 1:
                        if len(self.most_viable_attacks) == 1:
                            yield (t.name, self.most_viable_attacks[0].name, 
                                    lambda a, d: a > d, None)
                        else:
                            total = sum(a.forces for a in self.most_viable_attacks)
                            for adj in self.most_viable_attacks:
                                yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                                    lambda a: 1)
            else:
                return
        for t in player.territories:
            if t.forces > 1:
                adjacent = []
                if len(self.eliminate_territories) > 0:
                    adjacent = self.eliminate_territories
                elif len(self.areas_opportunity) > 0:
                    adjacent = self.areas_opportunity
                elif len(self.crucial_attack) > 0:
                    adjacent = self.crucial_attack
                elif len(self.annex_territory) > 0:
                    adjacent = self.annex_territory
                elif len(self.territories_attack) > 0:
                    adjacent = self.territories_attack
                else:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3]
                if len(adjacent) == 1:
                    yield (t.name, adjacent[0].name, 
                            lambda a, d: a > d, None)
                else:
                    total = sum(a.forces for a in adjacent)
                    for adj in adjacent:
                        yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                               lambda a: 1)

    def freemove(self, world, player, intents):
        self.analyse_intents(intents, player)
        if self.is_threatened:
            min_centrality = 99999
            territory_to_reinforce = None
            for t in player.territories:
                if self.key_value[t.name] < min_centrality:
                    min_centrality = self.key_value[t.name]
                    territory_to_reinforce = t
            srcs = sorted([t for t in player.territories if not t.border], 
                      key=lambda x: x.forces)
            if srcs:
                src = srcs[-1]
                n = src.forces - 1
                return (src, territory_to_reinforce, n)
        srcs = sorted([t for t in player.territories if not t.border], 
                      key=lambda x: x.forces)
        dests = []
        dests.extend(self.vulnerable)
        dests.extend(self.perceived_threat)
        dests.extend(self.territories_reinforce)
        if srcs:
            src = srcs[-1]
            n = src.forces - 1
            if len(dests) == 0:
                return (src, self.priority(world, player)[0], n)
            else:
                return (src, dests[0], n)
        return None

    def analyse_intents(self, intents, player):
        self.eliminate_territories = []
        self.vulnerable = []
        self.continents_priority = {}
        self.territories_reinforce = []
        self.territories_attack = []
        self.crucial_attack = []
        self.areas_under_threat = []
        self.areas_opportunity = []
        self.perceived_threat = []
        self.create_stronghold = []
        self.most_viable_attacks = []
        self.annex_territory = []
        intent_types = [
                "conquer_one_territory"
                ,"occupy_continent"
                ,"fortress_continent"
                ,"maximise_num_units_in_territory"
                ,"occupy_territory_enemy_continent"
                ,"eliminate_enemy_player"
            ]
        for area in self.world.areas.values():
            self.continents_priority[area.name] = 0
        for player_name, intent in intents:
            if player.name in intent['eliminate_enemy_player']:
                self.is_threatened = True
            for i in intent_types:
                self.check_is_attainable(player_name, i, intent[i], player)

        # print(self.eliminate_territories)
        print(self.vulnerable)
        print(self.continents_priority)
        print(self.territories_reinforce)
        print(self.territories_attack)
        print(self.crucial_attack)
        print(self.areas_under_threat)
        print(self.areas_opportunity)
        print(self.perceived_threat)
        print(self.create_stronghold)
        print(self.most_viable_attacks)
        print(self.annex_territory)
            

    def check_recursive(self, self_forces, opponent_forces,depth):
        if opponent_forces <= 0:
            return 1
        elif self_forces < opponent_forces + 3:
            return 0
        elif depth > 7:
            if opponent_forces < self_forces + 3:
                return 1
            else:
                return 0     
        elif self_forces > opponent_forces + 3:
            return .372*(self.check_recursive(self_forces, opponent_forces-2, depth+1)) + .292*(self.check_recursive(self_forces, opponent_forces-2, depth+1)) + .336*(self.check_recursive(self_forces-1, opponent_forces-1, depth+1))
        else:
            return 0

    def check_is_attainable(self, player_name, intent_type, intent, player):
        if intent_type=="eliminate_enemy_player" and not player.name in intent and len(intent) > 0:
            for t in player.territories:
                for o in t.adjacent():
                    if o.owner.name in intent and self.check_recursive( t.forces, o.forces, 1) > 0.5:
                        self.eliminate_territories.append(o)
        else:
            for t in player.territories:
                    for o in t.adjacent():
                        if o.owner.name == player_name and not t.owner.name == o.owner.name:
                            if self.check_recursive(o.forces, t.forces, 1) > 0.35:
                                self.vulnerable.append(t)
            self.vulnerable = compose(list, set)(self.vulnerable)
            if not ( len(self.crucial_attack) > 0 or len(self.territories_attack) > 0 or len(self.territories_reinforce) > 0):
                for t in player.territories:
                    for o in t.adjacent():
                        if player_name == player.name:
                            if self.check_recursive(t.forces, o.forces,1) > 0.6:
                                if o.name in self.crucial:
                                    self.crucial_attack.append(o)
                                else:
                                    self.territories_attack.append(o)
                            else:
                                self.territories_reinforce.append(t)
                self.crucial_attack = compose(list, set)(self.crucial_attack)
                self.territories_attack = compose(list, set)(self.territories_attack)
                self.territories_reinforce = compose(list, set)(self.territories_reinforce)
            if intent_type == "occupy_continent":
                if not player_name == player.name:
                    for t in self.territories_reinforce:
                        if t.area.name in [x[1] for x in intent]:
                            self.areas_under_threat.append(t)
                    self.areas_under_threat = compose(list, set)(self.areas_under_threat)
                else:
                    for t in self.territories_attack:
                        if t.area.name in [x[1] for x in intent]:
                            self.areas_opportunity.append(t)
                    self.areas_opportunity = compose(list, set)(self.areas_opportunity)
            elif intent_type == "fortress_continent":
                if not player_name == player.name:
                    for t in self.territories_reinforce:
                        if t.area.name in [x[1] for x in intent]:
                            self.perceived_threat.append(t)
                    self.perceived_threat = compose(list, set)(self.perceived_threat)
                else:
                    for t in self.territories_attack:
                        if t.area.name in [x[1] for x in intent]:
                            self.create_stronghold.append(t)
                    self.create_stronghold = compose(list, set)(self.create_stronghold)
            elif intent_type == "maximise_num_units_in_territory":
                print("maximise_num_units_in_territory", intent)
            elif intent_type == "occupy_territory_enemy_continent":
                if player_name == player.name:
                    for t in player.territories:
                        for adj in t.adjacent():
                            if not t.area.name == adj.area.name and (adj in self.crucial_attack or adj in self.territories_attack):
                                self.annex_territory.append(adj)
                self.annex_territory = compose(list, set)(self.annex_territory)
            elif intent_type == "conquer_one_territory":
                if player_name == player.name:
                    self.most_viable_attacks.extend(self.crucial_attack)
                    self.most_viable_attacks.extend(self.territories_attack)
    
    def build_strategy(self, intent):
        steps = []

def compose(g, f):
    def h(x):
        return g(f(x))
    return h

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 