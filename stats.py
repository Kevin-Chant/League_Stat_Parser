import os.path
from collections import defaultdict
import riot_api_access as riot
from global_defs import *
from helpers import *

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
		converted_cs = convert_cs_diff(participant_obj["timeline"]["creepsPerMinDeltas"].copy(), match_obj["gameDuration"])
		if opponent and participant_obj["timeline"]["lane"] != "JUNGLE":
			opponent_cs = convert_cs_diff(opponent["timeline"]["creepsPerMinDeltas"].copy(), match_obj["gameDuration"])
			if "10-20" in converted_cs:
				to_rtn["CS d@20"] = converted_cs["0-10"] + converted_cs["10-20"] - opponent_cs["0-10"] - opponent_cs["10-20"]
			elif "10-end" in converted_cs:
				to_rtn["CS d@20"] = converted_cs["0-10"] + converted_cs["10-end"] - opponent_cs["0-10"] - opponent_cs["10-end"]
			else:
				to_rtn["CS d@20"] = converted_cs["0-10"] - opponent_cs["0-10"]
		else:
			to_rtn["CS d@20"] = 0
		to_rtn["CS per min"] = round(float(to_rtn["Total CS"])/(match_obj["gameDuration"]/60), 2)
		to_rtn["Dmg dealt to champions"] = participant_obj["stats"]["totalDamageDealtToChampions"]
		to_rtn["DPM"] = round(float(to_rtn["Dmg dealt to champions"]/to_rtn["Time played"])*60, 2)
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
	except Exception as e:
		print("Errored on stats for match " + str(match_obj["gameId"]) + ", pid " + str(participant_id))
		print(e)
		exit(0)

def add_match_results_to_player_stats(curr_stats, existing_stats):
	agg = defaultdict(lambda: None)
	for key in OVERALL_STATS:
		agg[key] = OVERALL_STAT_AGG_FUNCS[key](curr_stats, existing_stats)
	return agg

def stats_from_filtered_matches(match_ids, summoner_name, key_hierarchy_list, desired_value_list, lane_role):
	aggregate_stats = defaultdict(lambda: 0)
	for match_id in match_ids:
		match_obj = riot.get_match_from_id(match_id)
		if match_obj["gameDuration"] < 600:
			continue
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

def get_and_cache_user_history(summonername, start_epoch=None, end_epoch=None, champion=None, lane_role=None):
    aid = riot.get_account_id(summonername)
    history = riot.get_match_history(aid, start_epoch, end_epoch, champion)["matches"]
    stats = stats_from_filtered_matches([match["gameId"] for match in history], summonername, [], [], lane_role)
    return stats