def recursive_generate_row_data(nested_dict, depth=0, row_list=[[]]):
    if isinstance(nested_dict, list):
        [row_list[depth].append(item) for item in nested_dict]
    else:
        if len(row_list) == depth+1:
            row_list.append([])
        for key in nested_dict:
            row_list[depth].append(key)
            recursive_generate_row_data(nested_dict[key], depth+1, row_list)
    return row_list


from collections import OrderedDict        
PLAYER_STATS_KEY_HIERARCHY = OrderedDict([  ("Combat Stats", ["Kills", "Deaths", "Assists", "KDA", "Kill Participation", "Kill Share", "Team Kills", "Enemy Kills", "Death Share", "Largest MultiKill", "Longest Killing Spree"]),
                                            ("Damage Stats", ["Objective Damage", "Turret Damage", "Total CC duration", "Dmg taken per min by min", "Dmg taken diff per min by min", "Heals Given", "Damage type breakdown"]),
                                            ("Vision Stats", OrderedDict([  ("Player", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Opponent", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Absolute Difference", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Relative Score", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"])
                                                    ])
                                            ),
                                            ("CS stats", ["Total CS", "CS per min", "CS per min by min", "CS differential", "CS differential by min"])
                                ])

print(is_tier(PLAYER_STATS_KEY_HIERARCHY, 4))
print(flatten_to_tier(PLAYER_STATS_KEY_HIERARCHY, 0))
# row_list = recursive_generate_row_data(PLAYER_STATS_KEY_HIERARCHY)
# for row in row_list:
#     print(row)
#     print("\n")
