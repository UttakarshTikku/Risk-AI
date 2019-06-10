import collections
import heapq
import random
from operator import attrgetter

import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph


class Decision_Engine(object):
    def __init__(self, steps, world, deceptive = False, strategies = 0):
        self.world = world
        self.deceptive = deceptive
        self.strategies = strategies
        self.setup()
        weighted_G=nx.Graph()
        for a in world.areas:
            for t in world.areas[a].territories:
                for adj in t.adjacent():
                    self.G.add_edge(t.name, adj.name)
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
        self.crucial = compose(list,set)(temp)
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

    def reinforce(self, available, world, player, intents, predictions):
        self.analyse_intents(intents, player)
        self.build_strategy( world, player, predictions)
        result = collections.defaultdict(int)
        if self.is_threatened:
            available, result = self.reinforce_safest_territory(player, available, result)
        available, result = self.reinforce_from_list(available, self.deceptive_reinforce, result)
        available, result = self.reinforce_from_list(available, self.strategic_reinforce, result)
        available, result = self.reinforce_from_list(available,self.vulnerable, result)
        available, result = self.reinforce_from_list(available,self.perceived_threat, result)
        available, result = self.reinforce_from_list(available,self.territories_reinforce, result)   
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

    def reinforce_safest_territory(self, player, available, result):
        min_centrality = 99999
        territory_to_reinforce = None
        for t in player.territories:
            if self.key_value[t.name] < min_centrality:
                min_centrality = self.key_value[t.name]
                territory_to_reinforce = t
        result[territory_to_reinforce] += available
        return (0, result)

    def reinforce_from_list(self, available, list_of_territories, result):
        for t in list_of_territories:
            if self.is_island_check(t):
                continue
            if not available > 0:
                break
            else:
                for adj in t.adjacent():
                    if t in result:
                        break
                    if not t.owner.name == adj.owner.name:
                        temp = available
                        for i in range(1,temp):
                            if self.check_recursive(t.forces + i, adj.forces) > 0.5 or i == temp:
                                result[t] += i
                                available = available - i
                                break
        return (available, result)

    def attack(self, world, player, intents, predictions):
        self.analyse_intents(intents, player)
        self.build_strategy( world, player, predictions)
        for t in player.territories:
            if t.forces > 1:
                adjacent = []
                if self.is_island_check(t):
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3]
                if self.is_threatened and len(self.most_viable_attacks) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.most_viable_attacks]
                if len(intersection(self.eliminate_territories, t.adjacent())) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.eliminate_territories]
                if len(adjacent) < 1 and len(intersection(self.areas_opportunity, t.adjacent())) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.areas_opportunity]
                if len(adjacent) < 1 and len(intersection(self.crucial_attack, t.adjacent())) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.crucial_attack]
                if len(adjacent) < 1 and len(intersection(self.annex_territory, t.adjacent())) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.annex_territory]
                if len(adjacent) < 1 and len(intersection(self.territories_attack, t.adjacent())) > 0:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3 and a in self.territories_attack]
                if len(adjacent) < 1:
                    adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3]
                if len(adjacent) == 1:
                    yield (t.name, adjacent[0].name, 
                            lambda a, d: a > d, None)
                else:
                    total = sum(a.forces for a in adjacent)
                    for adj in adjacent:
                        if adj.name in self.deceptive_attack:
                            yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                                lambda a: 1)
                    for adj in adjacent:
                        if adj.name in self.strategic_attack:
                            yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                                lambda a: 1)
                    for adj in adjacent:
                        yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                               lambda a: 1)

    def freemove(self, world, player, intents, predictions):
        self.analyse_intents(intents, player)
        self.build_strategy( world, player, predictions)
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
        if len(self.deceptive_retreat) > 0:
            territory_to_reinforce = self.deceptive_retreat[0]
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
        self.reset_state()
        for area in self.world.areas.values():
            self.continents_priority[area.name] = 0
        self.state_builder(player)
        for player_name, intent in intents:
            if player.name in intent['eliminate_enemy_player']:
                self.is_threatened = True
            for i in self.intent_types:
                getattr(self,i+"_check")(player_name, i, intent[i], player)

    def state_builder(self, player):
        for t in player.territories:
            for o in t.adjacent():
                if not t.owner.name == o.owner.name:
                    if self.check_recursive(o.forces, t.forces) > 0.35:
                        self.vulnerable.append(t)
        self.vulnerable = compose(list, set)(self.vulnerable)
        for t in player.territories:
            for o in t.adjacent():
                if not o.owner == player.name:
                    if self.check_recursive(t.forces, o.forces) > 0.6:
                        if o.name in self.crucial:
                            self.crucial_attack.append(o)
                        else:
                            self.territories_attack.append(o)
                    else:
                        self.territories_reinforce.append(t)
        self.crucial_attack = compose(list, set)(self.crucial_attack)
        self.territories_attack = compose(list, set)(self.territories_attack)
        self.territories_reinforce = compose(list, set)(self.territories_reinforce)

    def conquer_one_territory_check(self,  player_name, intent_type, intent, player):
        if player_name == player.name:
            self.most_viable_attacks.extend(self.crucial_attack)
            self.most_viable_attacks.extend(self.territories_attack)
    
    def occupy_continent_check(self,  player_name, intent_type, intent, player):
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
        
    def fortress_continent_check(self,  player_name, intent_type, intent, player):
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
    
    def maximise_num_units_in_territory_check(self,  player_name, intent_type, intent, player):
        # print(4)
        return

    def occupy_territory_enemy_continent_check(self,  player_name, intent_type, intent, player):
        if player_name == player.name:
            for t in player.territories:
                for adj in t.adjacent():
                    if not t.area.name == adj.area.name and (adj in self.crucial_attack or adj in self.territories_attack):
                        self.annex_territory.append(adj)
        self.annex_territory = compose(list, set)(self.annex_territory)
        
    def eliminate_enemy_player_check(self,  player_name, intent_type, intent, player):
        if not player.name in intent and len(intent) > 0:
            for t in player.territories:
                for o in t.adjacent():
                    if o.owner.name in intent and self.check_recursive( t.forces, o.forces) > 0.5:
                        self.eliminate_territories.append(o)

    def check_recursive(self, self_forces, opponent_forces):
        if (self_forces, opponent_forces) in self.memoise_recursion.keys():
            return self.memoise_recursion[(self_forces, opponent_forces)]
        elif (opponent_forces,self_forces) in self.memoise_recursion.keys():
            return 1-self.memoise_recursion[(opponent_forces,self_forces)]
        if opponent_forces <= 0:
            return 1
        elif self_forces < opponent_forces + 3:
            return 0 
        elif self_forces > opponent_forces + 3:
            self.memoise_recursion[(self_forces, opponent_forces)] = .372*(self.check_recursive(self_forces, opponent_forces-2)) + .292*(self.check_recursive(self_forces, opponent_forces-2)) + .336*(self.check_recursive(self_forces-1, opponent_forces-1))
            return self.memoise_recursion[(self_forces, opponent_forces)]
        else:
            return 0

    def build_strategy(self, world, player, predictions):
        temp = {}
        for p in predictions:
            if not p[0] == player.name:
                for k in p[1]:
                    if p[1][k][0]:
                        val = k.split('_',1)[1]
                        if val in ['eliminate_enemy_player', 'conquer_one_territory']:
                            temp[val] = True
                            continue
                        val = val.rsplit('_',1)
                        if val[0] in temp.keys():
                            temp[val[0]].append(val[1])
                        else:
                            temp[val[0]] = [val[1]]
        if self.deceptive:
            if self.strategies % 2 == 1:
                self.strategise_enemy_fault_lines(world, player)
            if (self.strategies/2) % 2 == 1:
                self.strategise_encirclement(world, player)
            if (self.strategies/4) % 2 == 1:
                self.strategise_feigned_retreat(world,player)

        self.strategic_attack_defence(temp, 'fortress')
        self.strategic_attack_defence(temp, 'occupy')
        self.strategic_attack_defence(temp, 'occupy_territory')
        self.strategic_attack_defence(temp, 'maximise_num_units_in')
        self.strategic_attack = compose(list, set)(self.strategic_attack)
        self.strategic_reinforce = compose(list, set)(self.strategic_reinforce)

    def strategic_attack_defence(self, temp, key):
        if key in temp.keys() and len(temp[key]) > 0:
            for t in self.vulnerable:
                if t.area.name in temp[key]:
                    self.strategic_reinforce.append(t)
            for t in self.perceived_threat:
                if t.area.name in temp[key]:
                    self.strategic_reinforce.append(t)
            for t in self.territories_reinforce:
                if t.area.name in temp[key]:
                    self.strategic_reinforce.append(t)
            for t in self.most_viable_attacks:
                if t.area.name in temp[key]:
                    self.strategic_attack.append(t)
            for t in self.eliminate_territories:
                if t.area.name in temp[key]:
                    self.strategic_attack.append(t)
            for t in self.crucial_attack:
                if t.area.name in temp[key]:
                    self.strategic_attack.append(t)
            for t in self.annex_territory:
                if t.area.name in temp[key]:
                    self.strategic_attack.append(t)
            for t in self.territories_attack:
                if t.area.name in temp[key]:
                    self.strategic_attack.append(t)

    def is_island_check(self, t):
        for adj in t.adjacent():
            if adj.owner == t.owner:
                return False
        return True

    def is_island_candidate(self, t):
        count = 0
        for adj in t.adjacent():
            if adj.owner == t.owner:
                count +=1
                if count > 1:
                    return False
        return True

    def is_one_hop_away(self, t):
        for adj in t.adjacent():
            terr = []
            for i in adj.adjacent():
                if i.owner == t.owner:
                    terr.append(adj)
            if len(terr) > 0:
                return terr
        return []

    def reset_state(self):
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
        self.is_threatened = False
        self.strategic_attack = []
        self.strategic_reinforce = []
        self.deceptive_attack = []
        self.deceptive_reinforce = []
        self.deceptive_retreat = []

    def setup(self):
        self.crucial = []
        self.memoise_recursion = {}
        self.G=nx.Graph()
        self.area_centrality = []
        self.reset_state()
        self.fault_line = []
        self.intent_types = [
                "conquer_one_territory"
                ,"occupy_continent"
                ,"fortress_continent"
                ,"maximise_num_units_in_territory"
                ,"occupy_territory_enemy_continent"
                ,"eliminate_enemy_player"
            ]

    def strategise_enemy_fault_lines(self, world, player):
        possible_sources_and_sinks = []
        territory_graph= nx.DiGraph()
        for a in world.areas:
            for t in world.areas[a].territories:
                for adj in t.adjacent():
                    if not adj.owner.name == player.name and not t.owner.name == player.name:
                        territory_graph.add_edge(t.name, adj.name, capacity=-adj.forces)
                        possible_sources_and_sinks.append(adj)
        possible_sources_and_sinks = compose(list, set)(possible_sources_and_sinks)
        graphs=list(nx.strongly_connected_component_subgraphs(territory_graph))
        fault_lines = []
        for g in graphs:
            sources_and_sinks_in_graph = [p for p in possible_sources_and_sinks if p.name in g.nodes()]
            ordered_pairs = []
            for s in sources_and_sinks_in_graph:
                for d in sources_and_sinks_in_graph:
                    if not s.name == d.name:
                        ordered_pairs.append((s,d))
            for s,d in ordered_pairs:
                flow_value, flow_dict = nx.maximum_flow(g, s.name, d.name)
                fault_lines.append((flow_value, flow_dict))
        paths = []
        for (f,p) in fault_lines:
            paths.append(unwrap_dict_of_dicts(p))
        shortest_fault_line = []
        shortest_fault_line_length = 50
        for p in paths:
            if len(p) < shortest_fault_line_length:
                shortest_fault_line_length = len(p)
                shortest_fault_line = p
        self.fault_line = shortest_fault_line
        self.deceptive_attack.extend(self.fault_line)

    def strategise_encirclement(self, world, player):
        self_islands = []
        opponent_islands  = []
        self_island_candidates = []
        opponent_island_candidate = []
        for area in world.areas:
            for t in world.areas[area].territories:
                if self.is_island_check(t):
                    if t.owner == player:
                        self_islands.append(t)
                    else:
                        opponent_islands.append(t)
                if self.is_island_candidate(t):
                    if t.owner == player:
                        self_island_candidates.append(t)
                    else:
                        opponent_island_candidate.append(t)
        attack = []
        reinforce = []
        for i in self_islands:
            join_mainland = False
            for t in i.adjacent():
                if self.check_recursive(i.forces, t.forces) > 0.5:
                    attack.append(t)
                    join_mainland = True
                    continue
            if not join_mainland and len(self.is_one_hop_away(i)) > 0:
                reinforce.append(i)
        for i in opponent_islands:
            opp = self.is_one_hop_away(i)
            if len(opp) > 0:
                reinforce.append(opp[0])
            else:
                attack_feasible = False
                max_forces = 0
                max_forces_terr = None
                for adj in i.adjacent():
                    if adj.forces > max_forces:
                        max_forces = adj.forces
                        max_forces_terr = adj
                    if self.check_recursive(adj.forces, i.forces) > 0.5:
                        attack_feasible = True
                        attack.append(i)
                        break
                if not attack_feasible and not max_forces_terr == None:
                    reinforce.append(max_forces_terr)
        for i_candidate in self_island_candidates:
            for adj in i_candidate.adjacent():
                if i_candidate.owner == adj.owner:
                    reinforce.append(adj)
        for i_candidate in opponent_island_candidate:
            for adj in i_candidate.adjacent():
                if i_candidate.owner == adj.owner:
                    attack.append(adj)
        self.deceptive_attack.extend(attack)
        self.deceptive_reinforce.extend(reinforce)

    def strategise_feigned_retreat(self,world, player):
        self_border = {}
        opponent_border = {}
        for t in player.territories:
            for adj in t.adjacent():
                if adj.owner != t.owner:
                    if t in self_border.keys():
                        self_border[t].append(adj)
                    else:
                        self_border[t] = [adj]
                    if adj in opponent_border.keys():
                        opponent_border[adj].append(t)
                    else:
                        opponent_border[adj] = [t]
        attack = []
        reinforce = []
        retreat = []
        for t in self_border.keys():
            temp = self_border[t]
            if len(temp) > 1:
                reinforce.append(t)
            elif self.check_recursive(t.forces, temp[0].forces) > 0.5:
                attack.append(temp[0])
        for t in opponent_border.keys():
            temp = opponent_border[t]
            Xsection = temp[0].adjacent()
            if len(temp) > 1:
                for x in temp:
                    Xsection = intersection(Xsection, x.adjacent())
                if len(Xsection) > 0:
                    for xs in Xsection:
                        if xs.owner == player:
                            reinforce.append(xs)
                            retreat.append(xs)
                            break
                else:
                    attack.append(t)
            else:
                reinforce.append(temp[0])
        self.deceptive_attack.extend(compose(list, set)(attack))
        self.deceptive_reinforce.extend(compose(list, set)(reinforce))
        self.deceptive_retreat = compose(list, set)(retreat)
                    
def compose(g, f):
    def h(x):
        return g(f(x))
    return h

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def unwrap_dict_of_dicts(p):
    ret_value = []
    if not isinstance(p,dict):
        return ret_value
    for k in p.keys():
        temp = [k]
        temp.extend(unwrap_dict_of_dicts(p[k]))
        ret_value.extend(temp)
    return compose(list,set)(ret_value)
