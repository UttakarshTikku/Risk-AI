import collections
"""
This module is used to compare the past two observed sets of world state indicators to
ascertain how the previous turn was resolved by the opponent. This helps to develop the
inferential process and create training data for the intent classifier.
"""

# This method receives old and new world state indicators and returns the resolution
# of that turn as a resilt. It takes the help from the previous_move_method
def find_previous_move_results(old_state, new_state, whoami, world):
    if len(old_state) == 0:
        return
    resolution = []
    for old in old_state:
        for key1, val1 in old:
            if key1 == 'AI_NAME':
                for new in new_state:
                    for key2, val2 in new:
                        if key2 == 'AI_NAME' and val2 == val1:
                            resolution.append((val1, previous_move(old, new, world)))
    return resolution


# This method receives the different keys of the world state indicators as input and 
# compares them individually
def previous_move(old, new, world):
    results = get_empty_result_structure(world)
    for key1, val1 in old:
        for key2, val2 in new:
            if key1 == key2:
                if key1 == "TERRITORIES":
                    if val2 > val1:
                        if val1 > 36:
                            results["eliminated_enemy_player"] = True
                        results["conquered_one_territory"] = True
                elif "_TERRITORIES" in key1 and val2 > val1:
                    results["occupied_territory_"+key1.split('_')[0]] = True
                elif "_PERCENTAGE" in key1 and not val1 == 100 and val2 == 100:
                    results["occupied_"+key1.split('_')[0]] = True
                elif "_BORDER_FORCES" in key1 and val2 > val1:
                    results["fortressed_"+key1.split('_')[0]] = True
                elif "_BORDER_FORCES" not in key1 and "_FORCES" in key1 and val2 > val1:
                    results["maximised_num_units_in_"+key1.split('_')[0]] = True
    return results

# Creates an empty placeholder for the previous turn resolution                
def get_empty_result_structure(world):
    results = {}
    results["eliminated_enemy_player"] = False
    results["conquered_one_territory"] = False
    for area in world.areas:
        results["occupied_territory_"+area] = False
        results["occupied_"+area] = False
        results["fortressed_"+area] = False
        results["maximised_num_units_in_"+area] = False
    return results

# This method merges the intended and actual intents before storing them 
# in the CSV files for future learnings.
# It is not directly used for decision making.
def merge_intended_and_actual(ai_name, intent, result, world):
    temp = {}
    temp["AI_NAME"] = ai_name
    intent = expand_intent(intent,world)
    temp = Merge(temp, Merge(collections.OrderedDict(sorted(intent.items())),collections.OrderedDict(sorted(result.items()))))
    return temp

# This method adapts the actual intent of the agents 
# in a format suitable for merging with results.
# It is not directly used for decision making.
def expand_intent(intent,world):
    temp = {}
    temp["conquer_one_territory"] = intent["conquer_one_territory"]
    temp["eliminate_enemy_player"] = 1 if len(intent["eliminate_enemy_player"]) > 0 else 0
    temp["occupy_territory_enemy_continent"] = intent["occupy_territory_enemy_continent"]
    for area in world.areas:
        temp["fortress_"+area] = 0
        temp["maximise_num_units_in_"+area] = 0
        temp["occupy_"+area] = 999999
    for x,y in intent["fortress_continent"]:
        temp["fortress_"+y] = x
    for x,y in intent["maximise_num_units_in_territory"]:
        temp["maximise_num_units_in_"+y] = x
    for x,y in intent["occupy_continent"]:
        temp["occupy_"+y] = x
    return temp

# A utility method to merge dictionaries
def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res