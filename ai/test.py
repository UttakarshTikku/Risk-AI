from ai import AI
import random
import collections

class TestAI(AI):
    """
    BetterAI: Thinks about what it is doing a little more - picks a priority
    continent and priorities holding and reinforcing it.
    """
    def start(self):
        self.area_priority = self.area_priority_gen()

    def area_priority_gen(self):
        world_areas_list = []
        for x in self.world.areas.values():
            outVal = 1
            playerAcquired = len(x.territories) + 1
            occupationForces = 1
            playerForces = 1
            for territory in x.territories:
                for out in territory.connect :
                    if out not in list(self.player.territories):
                        occupationForces += out.forces
                    else : 
                        playerForces += out.forces
                    if out not in x.territories or out not in list(self.player.territories):
                        outVal += 1
                if territory not in list(self.player.territories):
                    playerAcquired -= 1   
            world_areas_list.append( (x.name, (outVal*playerAcquired*(occupationForces-playerForces)/(len(x.territories)*x.value*occupationForces))))
        world_areas_list = sorted(world_areas_list, key=lambda element: (element[1], element[0]))
        return [ x for x,y in world_areas_list ]

    def priority(self):
        self.area_priority = self.area_priority_gen()
        priority = sorted([t for t in self.player.territories if t.border], 
                          key=lambda x: self.area_priority.index(x.area.name))
        # print("1", priority)
        priority = [t for t in priority if t.area == priority[0].area]
        # print("2", priority)
        return priority if priority else list(self.player.territories)
            

    def initial_placement(self, empty, available):
        if empty:
            empty = sorted(empty, key=lambda x: self.area_priority.index(x.area.name))
            return empty[0]
        else:
            return random.choice(self.priority())

    def reinforce(self, available):
        priority = self.priority()
        result = collections.defaultdict(int)
        while available:
            result[random.choice(priority)] += 1
            available -= 1
        return result

    def attack(self):
        for t in self.player.territories:
            if t.forces > 1:
                adjacent = [a for a in t.connect if a.owner != t.owner and t.forces >= a.forces + 3]
                if len(adjacent) == 1:
                        yield (t.name, adjacent[0].name, 
                               lambda a, d: a > d, None)
                else:
                    total = sum(a.forces for a in adjacent)
                    for adj in adjacent:
                        yield (t, adj, lambda a, d: a > d + total - adj.forces + 3, 
                               lambda a: 1)
    
    def freemove(self):
        srcs = sorted([t for t in self.player.territories if not t.border], 
                      key=lambda x: x.forces)
        if srcs:
            src = srcs[-1]
            n = src.forces - 1
            return (src, self.priority()[0], n)
        return None

                
                
                

    
            

                
    
