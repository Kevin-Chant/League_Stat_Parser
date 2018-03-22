import json
import os.path
from riot_api_access import *


def store_json(json_obj, filename, force=False):
	if os.path.isfile(filename) and not force:
		print("Cannot store at " + filename + ".\nFile already exists.")
		return False
	if not isinstance(json_obj, dict):
		print("Must be given a valid dictionary to store")
		return False
	with open(filename, 'w') as fp:
		json.dump(json_obj, fp)
		return True

def load_json(filename):
	if not os.path.isfile(filename):
		print("File cannot be found")
		return None
	with open(filename) as fp:
		return json.load(fp)

def update_champ_ids(force=False):
	dct = get_champion_id_dict()
	if not store_json(dct, "champ_ids.json", force):
		return None
	return dct


def find_id_in_list(id, fieldname, lst):
	for dct in lst:
		if dct[fieldname] == id:
			return dct

def find_matching_fields_in_list(value, fieldname, lst):
	matches = []
	for dct in lst:
		if dct[fieldname] == value:
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

def aggregate_cs_stats(prev_agg, new_stats):
	return None

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
	return {"KDA": new_kda,
	 		"Kills": new_kills,
	 		"Deaths": new_deaths,
	 		"Assists": new_assists,
	 		"Kill Participation": new_kp,
	 		"Kill Share": new_ks,
	 		"Death Share": new_ds,
	 		"Longest Killing Spree": new_killspree,
	 		"Largest MultiKill": new_multi,
	 		"Team Kills": new_t_kills,
	 		"Enemy Kills": new_e_kills
	 		}

def flatten(d, leaves={}):
	for k in d:
		if isinstance(d[k], dict):
			flatten(d[k], leaves)
		else:
			leaves[k] = d[k]
	return leaves

def get_all_player_stats(match_obj, participant_id):
	c_stats = get_combat_stats(match_obj, participant_id)
	d_stats = get_damage_stats(match_obj, participant_id)
	d_bkdn = get_damage_breakdown(match_obj, participant_id)
	v_stats = get_vision_stats(match_obj, participant_id)
	cs_stats = get_cs_stats(match_obj, participant_id)
	return {**flatten(c_stats), **flatten(d_stats), **flatten(d_bkdn), **flatten(v_stats), **flatten(cs_stats)}
