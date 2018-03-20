import json
import os.path
from riot_api_access import *

def store_match(match_obj, filename):
	if os.path.isfile(filename):
		print("Cannot store at " + filename + ".\nFile already exists.")
		return False
	if not isinstance(match_obj, dict):
		print("Must be given a valid dictionary to store")
		return False
	with open(filename, 'w') as fp:
		json.dump(match_obj, fp)
		return True

def load_match(filename):
	if not os.path.isfile(filename):
		print("File cannot be found")
		return None
	with open(filename) as fp:
		return json.load(fp)

def find_id_in_list(id, fieldname, lst):
	for dct in lst:
		if dct[fieldname] == id:
			return dct

def convert_cs_diff(cs_diff_by_min, gamelength):
	for duration in cs_diff_by_min:
		if "end" not in duration:
			cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * 10, 2)
		else:
			cs_diff_by_min[duration] = round(cs_diff_by_min[duration] * float(gamelength-1800)/60, 2)
	return cs_diff_by_min

def get_partic_id_from_name(match_obj, summoner_name):
	for partic_identity in match_obj["participantIdentities"]:
		if "player" in partic_identity and "summonerName" in partic_identity["player"] and partic_identity["player"]["summonerName"] == summoner_name:
			return partic_identity["participantId"]
	return None

def get_opponent(participants, participant_id):
	participant_role = find_id_in_list(participant_id, "participantId", participants)["timeline"]["role"]
	for other in participants:
		if participant_id != other["participantId"] and other["timeline"]["role"] == participant_role:
			return other

def get_cs_stats(match_obj, participant_id):
	participant_obj = find_id_in_list(participant_id, "participantId", match_obj["participants"])
	cs_per_min_by_min = participant_obj["timeline"]["creepsPerMinDeltas"]
	cs_diff_by_min = convert_cs_diff(participant_obj["timeline"]["csDiffPerMinDeltas"], match_obj["gameDuration"])
	stats = participant_obj["stats"]
	total_cs = stats["totalMinionsKilled"] + stats["neutralMinionsKilled"]
	cs_per_min = round(float(total_cs)/(match_obj["gameDuration"]/60), 2)
	opponent = get_opponent(match_obj["participants"], participant_id)
	cs_diff = total_cs - opponent["stats"]["totalMinionsKilled"] - opponent["stats"]["neutralMinionsKilled"]
	return {"CS per min by min": cs_per_min_by_min, "CS differential by min": cs_diff_by_min, "Total CS": total_cs, "CS per min": cs_per_min, "CS differential": cs_diff}

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
	return {"KDA": kda, "Kills": kills, "Deaths": deaths, "Assists": assists, "Kill Participation": kill_partic, "Kill Share": kill_share, "Death Share": death_share, "Longest Killing Spree": killing_spree, "Largest MultiKill": multi_kill, "Team Kills": team_kills, "Enemy Kills": enemy_kills}

def aggregate_combat_stats(prev_agg, new_stats):
	new_kills = prev_agg["Kills"] + new_stats["Kills"]
	new_deaths = prev_agg["Deaths"] + new_stats["Deaths"]
	new_assists = prev_agg["Assists"] + new_stats["Assists"]
	new_t_kills = prev_agg["Team Kills"] + new_stats["Team Kills"]
	new_e_kills = prev_agg["Enemy Kills"] + new_stats["Enemy Kills"]
	new_kp = round(float(new_kills+new_assists)/new_t_kills, 2)
	new_ks = round(float(new_kills)/new_t_kills, 2)
	new_ds = round(float(new_deaths)/new_e_kills, 2)
	new_killspree = max(prev_agg["Longest Killing Spree"], new_stats["Longest Killing Spree"])
	new_multi = max(prev_agg["Largest MultiKill"], new_stats["Largest MultiKill"])
	new_kda = round(float(new_kills+new_assists)/new_deaths,2)
	return {"KDA": new_kda, "Kills": new_kills, "Deaths": new_deaths, "Assists": new_assists, "Kill Participation": new_kp, "Kill Share": new_ks, "Death Share": new_ds, "Longest Killing Spree": new_killspree, "Largest MultiKill": new_multi, "Team Kills": new_t_kills, "Enemy Kills": new_e_kills}


m = load_match("example_match.json")
# m2 = load_match("example_custom.json")
# combat_stats1 = get_combat_stats(m1, 1)
# combat_stats2 = get_combat_stats(m2, 1)
# print(combat_stats1)
# print("\n")
# print(combat_stats2)
# print("\n")
# print(aggregate_combat_stats(combat_stats1,combat_stats2))
partic_id = get_partic_id_from_name(m, "Gezang")
if partic_id:
	for key,val in get_combat_stats(m, partic_id).items():
		print(key + ": " + str(val))