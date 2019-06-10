import collections

def find_previous_move_results(old_state, new_state, whoami, world):
    if len(old_state) == 0:
        return
    return_val = []
    for old in old_state:
        for key1, val1 in old:
            if key1 == 'AI_NAME':
                for new in new_state:
                    for key2, val2 in new:
                        if key2 == 'AI_NAME' and val2 == val1:
                            return_val.append((val1, previous_move(old, new, world)))
    return return_val

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

def merge_intended_and_actual(ai_name, intent, result, world):
    temp = {}
    temp["AI_NAME"] = ai_name
    intent = expand_intent(intent,world)
    temp = Merge(temp, Merge(collections.OrderedDict(sorted(intent.items())),collections.OrderedDict(sorted(result.items()))))
    return temp

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

def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res