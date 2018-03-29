import os.path
from collections import defaultdict
from riot_api_access import *
from global_defs import *
import helpers


def find_id_in_list(id, fieldname, lst):
	for dct in lst:
		if str(dct[fieldname]).lower() == str(id).lower():
			return dct

def find_matching_fields_in_list(value, fieldname, lst):
	matches = []
	for dct in lst:
		if str(dct[fieldname]).lower() == str(value).lower():
			matches.append(dct)
	return matches

def get_subfields_in_list(fieldname, lst):
	fields = []
	for dct in lst:
		if fieldname in dct:
			fields.append(dct[fieldname])
	return fields

def convert_cs_diff(cs_diff_by_min, gamelength):
	for duration in cs_diff_by_min:
		if "end" not in duration:
			cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * 10, 2)
		else:
			cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * float(gamelength-int(duration[:2])*60)/60, 2)
	return cs_diff_by_min

def get_name_from_partic_id(match_obj, partic_id):
	partic_obj = find_id_in_list(partic_id, "participantId", match_obj["participantIdentities"])
	if "player" in partic_obj:
		return partic_obj["player"]["summonerName"]

def clean(name):
	return "".join(name.split(" ")).lower()

def get_partic_id_from_name(match_obj, summoner_name):
	for partic_identity in match_obj["participantIdentities"]:
		if "player" in partic_identity and "summonerName" in partic_identity["player"] and clean(partic_identity["player"]["summonerName"]) == clean(summoner_name):
			return partic_identity["participantId"]
	return None

def get_opponent(participants, participant_id):
	participant_role = find_id_in_list(participant_id, "participantId", participants)["timeline"]["role"]
	for other in participants:
		if participant_id != other["participantId"] and other["timeline"]["role"] == participant_role:
			return other

def get_basic_game_info(match_obj):
	blue_picks = get_subfields_in_list("championId", find_matching_fields_in_list(100, "teamId", match_obj["participants"]))
	red_picks = get_subfields_in_list("championId", find_matching_fields_in_list(200, "teamId", match_obj["participants"]))
	winner = "Blue" if match_obj["teams"][0]["win"] == "Win" else "Red"
	player_identities = get_subfields_in_list("player", match_obj["participantIdentities"])
	to_rtn = { 	"Blue bans": match_obj["teams"][0]["bans"],
				"Blue picks": blue_picks,
				"Red bans": match_obj["teams"][1]["bans"],
				"Red picks": red_picks,
				"Duration": match_obj["gameDuration"],
				"Winner": winner
				}
	if len(player_identities) > 0:
		to_rtn["Players"] = player_identities
	return to_rtn

def get_team_stats(match_obj, team_id):
	team = find_id_in_list(team_id, "teamId", match_obj["teams"])
	players = find_matching_fields_in_list(team_id, "teamId", match_obj["participants"])
	total_wards_placed = sum([player["stats"]["wardsPlaced"] for player in players])
	total_wards_killed = sum([player["stats"]["wardsKilled"] for player in players])
	total_pinks = sum([player["stats"]["visionWardsBoughtInGame"] for player in players])
	total_vision_score = sum([player["stats"]["visionScore"] for player in players])
	return { 	"Total wards placed": total_wards_placed,
				"Total control wards": total_pinks,
				"Total wards killed": total_wards_killed,
				"Total vision score": total_vision_score,
				"Tower kills": team["towerKills"],
				"Inhibitor kills":  team["inhibitorKills"],
				"Dragon kills": team["dragonKills"],
				"Baron kills": team["baronKills"],
				"Took Rift Herald": team["firstRiftHerald"],
				"Win": team["win"] != "Fail",
				"First tower": team["firstTower"],
				"First inhibitor": team["firstInhibitor"],
				"First dragon": team["firstDragon"],
				"First blood": team["firstBlood"],
				"First baron": team["firstBaron"],
				"Duration": match_obj["gameDuration"]
			}

def get_vision_stats(match_obj, participant_id):
	stats = find_id_in_list(participant_id, "participantId", match_obj["participants"])["stats"]
	opponent_stats = get_opponent(match_obj["participants"], participant_id)["stats"]
	return { 	"Player": { "Wards placed": stats["wardsPlaced"],
							"Wards killed": stats["wardsKilled"],
							"Vision score": stats["visionScore"],
							"Control wards purchased": stats["visionWardsBoughtInGame"]
							},
				"Opponent": { "Wards placed": opponent_stats["wardsPlaced"],
							"Wards killed": opponent_stats["wardsKilled"],
							"Vision score": opponent_stats["visionScore"],
							"Control wards purchased": opponent_stats["visionWardsBoughtInGame"]
							},
				"Absolute Difference": {"Wards placed": stats["wardsPlaced"] - opponent_stats["wardsPlaced"],
										"Wards killed": stats["wardsKilled"] - opponent_stats["wardsKilled"],
										"Vision score": stats["visionScore"] - opponent_stats["visionScore"],
										"Control wards purchased": stats["visionWardsBoughtInGame"] - opponent_stats["visionWardsBoughtInGame"]
									},
				"Relative Score": { "Wards placed": round(float(stats["wardsPlaced"])/max(opponent_stats["wardsPlaced"],1),2),
									"Wards killed": round(float(stats["wardsKilled"])/max(opponent_stats["wardsKilled"],1),2),
									"Vision score": round(float(stats["visionScore"])/max(opponent_stats["visionScore"],1),2),
									"Control wards purchased": round(float(stats["visionWardsBoughtInGame"])/max(opponent_stats["visionWardsBoughtInGame"],1),2)
									}

			}

def get_damage_stats(match_obj, participant_id):
	participant_obj = find_id_in_list(participant_id, "participantId", match_obj["participants"])
	stats = participant_obj["stats"]
	return {"Dmg taken per min by min": participant_obj["timeline"]["damageTakenPerMinDeltas"],
			"Dmg taken diff per min by min": participant_obj["timeline"]["damageTakenDiffPerMinDeltas"],
			"Objective Damage": stats["damageDealtToObjectives"],
			"Turret Damage": stats["damageDealtToTurrets"],
			"Heals Given": stats["totalHeal"],
			"Total CC duration": stats["timeCCingOthers"]
			}

def get_damage_breakdown(match_obj, participant_id):
	stats = find_id_in_list(participant_id, "participantId", match_obj["participants"])["stats"]
	return { "Dealt": { "Magic": stats["magicDamageDealt"],
						"Physical": stats["physicalDamageDealt"],
						"True": stats["trueDamageDealt"],
						"Total": stats["totalDamageDealt"]
						},
			"Taken": { 	"Magic": stats["magicalDamageTaken"],
						"Physical": stats["physicalDamageTaken"],
						"True": stats["trueDamageTaken"],
						"Total": stats["totalDamageTaken"]
						},
			"Dealt to Champions": {	"Magic": stats["magicDamageDealtToChampions"],
									"Physical": stats["physicalDamageDealtToChampions"],
									"True": stats["trueDamageDealtToChampions"],
									"Total": stats["totalDamageDealtToChampions"]
									}
			}


def get_cs_stats(match_obj, participant_id):
	participant_obj = find_id_in_list(participant_id, "participantId", match_obj["participants"])
	cs_per_min_by_min = participant_obj["timeline"]["creepsPerMinDeltas"]
	cs_diff_by_min = convert_cs_diff(participant_obj["timeline"]["csDiffPerMinDeltas"], match_obj["gameDuration"])
	stats = participant_obj["stats"]
	total_cs = stats["totalMinionsKilled"] + stats["neutralMinionsKilled"]
	cs_per_min = round(float(total_cs)/(match_obj["gameDuration"]/60), 2)
	opponent = get_opponent(match_obj["participants"], participant_id)
	cs_diff = total_cs - opponent["stats"]["totalMinionsKilled"] - opponent["stats"]["neutralMinionsKilled"]
	return { 	"CS per min by min": cs_per_min_by_min,
				"CS differential by min": cs_diff_by_min,
				"Total CS": total_cs,
				"CS per min": cs_per_min,
				"CS differential": cs_diff
			}

def get_combat_stats(match_obj, participant_id):
	participant_obj = find_id_in_list(participant_id, "participantId", match_obj["participants"])
	stats = participant_obj["stats"]
	kills = stats["kills"]
	deaths = stats["deaths"]
	assists = stats["assists"]
	team_kills = sum([p["stats"]["kills"] for p in match_obj["participants"] if p["teamId"] == participant_obj["teamId"]])
	enemy_kills = sum([p["stats"]["kills"] for p in match_obj["participants"] if p["teamId"] != participant_obj["teamId"]])
	kill_partic = round(float(kills+assists)/team_kills, 2)
	kill_share = round(float(kills)/team_kills, 2)
	death_share = round(float(deaths)/enemy_kills, 2)
	killing_spree = stats["largestKillingSpree"]
	multi_kill = stats["largestMultiKill"]
	kda = round(float(kills+assists)/deaths, 2)
	return { 	"KDA": kda,
				"Kills": kills,
				"Deaths": deaths,
				"Assists": assists,
				"Kill Participation": kill_partic,
				"Kill Share": kill_share,
				"Death Share": death_share,
				"Longest Killing Spree": killing_spree,
				"Largest MultiKill": multi_kill,
				"Team Kills": team_kills,
				"Enemy Kills": enemy_kills
			}

def flatten(d, leaves={}, prev_keys = []):
	for k in d:
		if isinstance(d[k], dict):
			flatten(d[k], leaves, prev_keys + [k])
		else:
			if len(prev_keys) > 0:
				leaves["_".join(prev_keys) + "_" + k] = d[k]
			else:
				leaves[k] = d[k]
	return leaves

def get_all_player_stats(match_obj, participant_id):
	c_stats = get_combat_stats(match_obj, participant_id)
	d_stats = get_damage_stats(match_obj, participant_id)
	d_bkdn = get_damage_breakdown(match_obj, participant_id)
	v_stats = get_vision_stats(match_obj, participant_id)
	cs_stats = get_cs_stats(match_obj, participant_id)
	return {**flatten({"Combat Stats": c_stats}), **flatten({"Dmg Stats": d_stats}), **flatten({"Dmg Breakdown": d_bkdn}), **flatten({"Vision Stats": v_stats}), **flatten({"CS Stats": cs_stats}), **flatten({"Player": get_name_from_partic_id(match_obj, participant_id)})}

def get_overall_player_stats(match_obj, participant_id=None, summoner_name=None, lane_role=None, teamId=None):
	try:
		to_rtn = {}
		if summoner_name and lane_role:
			to_rtn["Player"] = summoner_name
			matching_partic = find_matching_fields_in_list(lane_role[0], "lane", [participant["timeline"] for participant in match_obj["participants"]])
			matching_partic = find_matching_fields_in_list(lane_role[1], "role", matching_partic)
			participants = [find_id_in_list(m_p['participantId'], "participantId", match_obj["participants"]) for m_p in matching_partic]
			participant_obj = find_id_in_list(teamId, "teamId", participants)
			participant_id = participant_obj["participantId"]
		else:
			participant_obj = find_id_in_list(participant_id, "participantId", match_obj["participants"])
			to_rtn["Player"] = find_id_in_list(participant_id, "participantId", match_obj["participantIdentities"])["player"]["summonerName"]
		to_rtn["Number of games"] = 1
		if find_id_in_list(participant_obj["teamId"], "teamId", match_obj["teams"])["win"] == "Win":
			to_rtn["Winrate"] = 1.0
		else:
			to_rtn["Winrate"] = 0.0
		to_rtn["Time played"] = match_obj["gameDuration"]
		to_rtn["Kills"] = participant_obj["stats"]["kills"]
		to_rtn["Deaths"] = participant_obj["stats"]["deaths"]
		to_rtn["Assists"] = participant_obj["stats"]["assists"]
		to_rtn["KDA"] = round(float(to_rtn["Kills"] + to_rtn["Assists"])/max(to_rtn["Deaths"], 1), 2)
		to_rtn["Team Kills"] = sum(p["stats"]["kills"] for p in find_matching_fields_in_list(participant_obj["teamId"], "teamId", match_obj["participants"]))
		to_rtn["Kill Participation"] = round(float(to_rtn["Kills"] + to_rtn["Assists"])/to_rtn["Team Kills"], 2)
		to_rtn["Kill Share"] = round(float(to_rtn["Kills"])/to_rtn["Team Kills"], 2)
		to_rtn["Enemy Kills"] = sum(p["stats"]["kills"] for p in find_matching_fields_in_list(300-participant_obj["teamId"], "teamId", match_obj["participants"]))
		to_rtn["Death Share"] = round(float(to_rtn["Deaths"])/to_rtn["Enemy Kills"], 2)
		to_rtn["Largest MultiKill"] = participant_obj["stats"]["largestMultiKill"]
		to_rtn["Longest Killing Spree"] = participant_obj["stats"]["largestKillingSpree"]
		to_rtn["Total CS"] = participant_obj["stats"]["totalMinionsKilled"] + participant_obj["stats"]["neutralMinionsKilled"]
		opponent = get_opponent(match_obj["participants"], participant_id)
		converted_cs = convert_cs_diff(participant_obj["timeline"]["creepsPerMinDeltas"], match_obj["gameDuration"])
		if opponent and participant_obj["timeline"]["lane"] != "JUNGLE":
			opponent_cs = convert_cs_diff(opponent["timeline"]["creepsPerMinDeltas"], match_obj["gameDuration"])
			if "10-20" in converted_cs:
				to_rtn["CS d@20"] = converted_cs["0-10"] + converted_cs["10-20"] - opponent_cs["0-10"] - opponent_cs["10-20"]
			else:
				to_rtn["CS d@20"] = converted_cs["0-10"] + converted_cs["10-end"] - opponent_cs["0-10"] - opponent_cs["10-end"]
		else:
			to_rtn["CS d@20"] = 0
		to_rtn["CS per min"] = round(float(to_rtn["Total CS"])/(match_obj["gameDuration"]/60), 2)
		to_rtn["Dmg dealt to champions"] = participant_obj["stats"]["totalDamageDealtToChampions"]
		to_rtn["Dmg dealt"] = participant_obj["stats"]["totalDamageDealt"]
		to_rtn["Dmg taken"] = participant_obj["stats"]["totalDamageTaken"]
		to_rtn["Vision Score"] = participant_obj["stats"]["visionScore"]
		if opponent:
			to_rtn["Vision score diff"] = participant_obj["stats"]["visionScore"] - opponent["stats"]["visionScore"]
		else:
			to_rtn["Vision score diff"] = 0
		to_rtn["Control wards purchased"] = participant_obj["stats"]["visionWardsBoughtInGame"]
		to_rtn["Wards Placed"] = participant_obj["stats"]["wardsPlaced"]
		return to_rtn
	except:
		print("Errored on stats for match " + str(match_obj["gameId"]) + ", pid " + str(participant_id))
		exit(0)

def add_match_results_to_player_stats(curr_stats, existing_stats):
	agg = defaultdict(lambda: None)
	for key in OVERALL_STATS:
		agg[key] = OVERALL_STAT_AGG_FUNCS[key](curr_stats, existing_stats)
	return agg

def stats_from_filtered_matches(match_ids, summoner_name, key_hierarchy_list, desired_value_list, lane_role):
	aggregate_stats = defaultdict(lambda: 0)
	for match_id in match_ids:
		match_obj = helpers.download_match_with_cache(match_id)
		for i in range(len(key_hierarchy_list)):
			key_hierarchy = key_hierarchy_list[i]
			desired_value = desired_value_list[i]
			d = match_obj
			for key in key_hierarchy:
				if not key in d or (not isinstance(d[k], dict) and d[k] != desired_value):
					match_obj = None
		if not match_obj:
			continue
		if lane_role:
			pid = get_partic_id_from_name(match_obj, summoner_name)
			participant = find_id_in_list(pid, "participantId", match_obj["participants"])
			timeline = participant["timeline"]
			actual_lane = timeline["lane"]
			actual_role = timeline	["role"]
			if actual_lane != lane_role[0] and actual_role != lane_role[1]:
				continue
		match_stats = get_overall_player_stats(match_obj, participant_id = get_partic_id_from_name(match_obj, summoner_name))
		aggregate_stats = add_match_results_to_player_stats(match_stats, aggregate_stats)
	return aggregate_stats

