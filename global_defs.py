import riot_api_access as riot
from helpers import *

PLAYER_STATS_SPREADSHEET_ID = "1fu8T513ZZhWDn0Fimc01evXSW6lwxUJI49gHq_BUow8"
RMT_STATS_SHEET = "1haqC4FS0pY2bVe9agDLDi5KtMvk4hzRlcl9RvI-We4s"
STATS_TESTING_SHEET = "1MLtNlYn7TN-ef0f75zzWmTtO2sHEsKNv41D4dNU9awg"
CUSTOM_TEAM_BG_COLOR = {"red": "183", "green": "225", "blue": "205"}


def combine_players(x,y):
	if x["Player"] == y["Player"] or y["Player"] == 0:
		return x["Player"]
	else:
		raise ValueError("Aggregating stats from two players: " + x["Player"] + ", " + y["Player"])

OVERALL_STATS = ["Player", "Lane/Role", "Winrate", "Number of games", "Time played", "Kills", "Deaths", "Assists", "Kills per Game", "Deaths per Game", "Assists per Game", "KDA", "Kill Participation", "Kill Share", "Death Share", "Team Kills", "Enemy Kills", "Largest MultiKill", "Longest Killing Spree", "Total CS", "CS d@20", "CS per min", "Dmg dealt to champions", "Dmg dealt to champions per game", "DPM", "Dmg dealt", "Dmg dealt per game", "Dmg taken", "Dmg taken per game", "Vision Score", "Vision score diff", "Control wards purchased", "Control Wards per Game", "Wards Placed", "Wards Placed per Game"]
OVERALL_STAT_AGG_FUNCS = { 	"Player": lambda x,y: combine_players(x,y),
							"Lane/Role": lambda x,y: x["Lane/Role"],
							"Winrate": lambda x,y: round(float(x["Winrate"] * x["Number of games"] + y["Winrate"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"Number of games": lambda x,y: x["Number of games"] + y["Number of games"],
							"Time played": lambda x,y: x["Time played"] + y["Time played"],
							"Kills": lambda x,y: x["Kills"] + y["Kills"],
							"Kills per Game": lambda x,y: round(float(x["Kills"] + y["Kills"])/(x["Number of games"] + y["Number of games"]), 2),
							"Deaths": lambda x,y: x ["Deaths"] + y["Deaths"],
							"Deaths per Game": lambda x,y: round(float(x["Deaths"] + y["Deaths"])/(x["Number of games"] + y["Number of games"]), 2),
							"Assists": lambda x,y: x["Assists"] + y["Assists"],
							"Assists per Game": lambda x,y: round(float(x["Assists"] + y["Assists"])/(x["Number of games"] + y["Number of games"]), 2),
							"KDA": lambda x,y: round(float(x["Kills"]+x["Assists"]+y["Kills"]+y["Assists"])/max(x["Deaths"]+y["Deaths"], 1),2),
							"Kill Participation": lambda x,y: round(float(x["Kills"]+x["Assists"]+y["Kills"]+y["Assists"])/max(x["Team Kills"]+y["Team Kills"],1),2),
							"Kill Share": lambda x,y: round(float(x["Kills"]+y["Kills"])/max(x["Team Kills"]+y["Team Kills"],1),2),
							"Death Share": lambda x,y: round(float(x["Deaths"]+y["Deaths"])/max(x["Enemy Kills"]+y["Enemy Kills"],1),2),
							"Team Kills": lambda x,y: x["Team Kills"] + y["Team Kills"],
							"Enemy Kills": lambda x,y: x["Enemy Kills"] + y["Enemy Kills"],
							"Largest MultiKill": lambda x,y: max(x["Largest MultiKill"], y["Largest MultiKill"]),
							"Longest Killing Spree": lambda x,y: max(x["Longest Killing Spree"], y["Longest Killing Spree"]),
							"Total CS": lambda x,y: x["Total CS"] + y["Total CS"],
							"Avg CS": lambda x,y: round(float(x["Total CS"] + y["Total CS"])/(x["Number of games"] + y["Number of games"]),2),
							"CS d@20": lambda x,y: round(float(x["CS d@20"] * x["Number of games"] + y["CS d@20"] * y["Number of games"])/max(x["Number of games"] + y["Number of games"],1), 2),
							"CS per min":lambda x,y: round(float(x["CS per min"] * x["Time played"] + y["CS per min"] * y["Time played"])/max(x["Time played"] + y["Time played"],1), 2),
							"Dmg dealt to champions": lambda x,y: x["Dmg dealt to champions"] + y["Dmg dealt to champions"],
							"Dmg dealt to champions per game": lambda x,y: round(float(x["Dmg dealt to champions"] + y["Dmg dealt to champions"])/(x["Number of games"] + y["Number of games"]), 2),
							"DPM": lambda x,y: round(float(x["DPM"]*x["Time played"] + y["DPM"] * y["Time played"])/max(x["Time played"] + y["Time played"], 1),2),
							"Dmg dealt": lambda x,y: x["Dmg dealt"] + y["Dmg dealt"],
							"Dmg dealt per game": lambda x,y: round(float(x["Dmg dealt"] + y["Dmg dealt"])/(x["Number of games"] + y["Number of games"]), 2),
							"Dmg taken": lambda x,y: x["Dmg taken"] + y["Dmg taken"],
							"Dmg taken per game": lambda x,y: round(float(x["Dmg taken"] + y["Dmg taken"])/(x["Number of games"] + y["Number of games"]), 2),						
							"Vision Score": lambda x,y: round(float(x["Vision Score"] * x["Number of games"] + y["Vision Score"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"Vision score diff": lambda x,y: round(float(x["Vision score diff"] * x["Number of games"] + y["Vision score diff"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"Control wards purchased": lambda x,y: x["Control wards purchased"] + y["Control wards purchased"],
							"Control Wards per Game": lambda x,y: round(float(x["Control wards purchased"] + y["Control wards purchased"])/(x["Number of games"] + y["Number of games"]),2),
							"Wards Placed": lambda x,y: x["Wards Placed"] + y["Wards Placed"],
							"Wards Placed per Game": lambda x,y: round(float(x["Wards Placed"] + y["Wards Placed"])/(x["Number of games"] + y["Number of games"]),2)
							}
TRACKED_CHAMPION_STATS = ["Wins", "Losses", "Bans", "Num Games", "Total gametime", "Kills", "Deaths", "Assists", "Team Kills", "Enemy Kills", "Total CS", "Total CS diff @20", "Dmg to champs", "Dmg dealt", "Dmg taken"]
ON_DEMAND_CHAMPION_STATS = ["Presence", "Win %", "Kill Partic", "Kill Share", "Death Share", "Kills/game", "Deaths/game", "Assists/game", "Avg CS", "CS per min", "Avg CSD@20", "Dmg to champs per game", "Dmg dealt per game", "Dmg taken per game"]

def get_csd20(match, cid):
	p_ob =find_id_in_list(cid, "championId", match["participants"]) 
	opponent = get_opponent(match["participants"], p_ob["participantId"])
	to_rtn = 0
	cs = p_ob["timeline"]["creepsPerMinDeltas"].copy()
	if opponent and p_ob["timeline"]["lane"] != "JUNGLE":
		opponent_cs = opponent["timeline"]["creepsPerMinDeltas"].copy()
		gameDuration = match["gameDuration"]
		for duration in opponent_cs:
			if not "end" in duration:
				cs[duration] *= 10
				opponent_cs[duration] *= 10
			else:
				cs[duration] *= gameDuration/60 - int(duration[:2])
				opponent_cs[duration] *= gameDuration/60 - int(duration[:2])
		to_rtn = cs["0-10"] - opponent_cs["0-10"]
		if "10-20" in cs:
			to_rtn += cs["10-20"] - opponent_cs["10-20"]
		elif "10-end" in cs:
			to_rtn += cs["10-end"] - opponent_cs["10-end"]
	return to_rtn

BANNED_CHAMP_STATS = {	"Wins": 0,
						"Losses": 0,
						"Bans": 1,
						"Num Games": 0,
						"Total gametime": 0,
						"Kills": 0,
						"Deaths": 0,
						"Assists": 0,
						"Team Kills": 0,
						"Enemy Kills": 0,
						"Total CS": 0,
						"Total CS diff @20": 0,
						"Dmg to champs": 0,
						"Dmg dealt": 0,
						"Dmg taken": 0
						}

STAT_COLLECTION_METHODS = { "Wins": lambda match, cid: 1 if find_id_in_list(find_id_in_list(cid, "championId", match["participants"])["teamId"], "teamId", match["teams"])["win"] == "Win" else 0,
							"Losses": lambda match, cid: 1 if find_id_in_list(find_id_in_list(cid, "championId", match["participants"])["teamId"], "teamId", match["teams"])["win"] == "Fail" else 0,
							"Bans": lambda match, cid: 0,
							"Num Games": lambda match, cid: 1,
							"Total gametime": lambda match, cid: match["gameDuration"],
							"Kills": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["kills"],
							"Deaths": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["deaths"],
							"Assists": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["assists"],
							"Team Kills": lambda match, cid: sum([p["stats"]["kills"] for p in find_matching_fields_in_list(find_id_in_list(cid, "championId", match["participants"])["teamId"], "teamId", match["participants"])]),
							"Enemy Kills": lambda match, cid: sum([p["stats"]["kills"] for p in find_matching_fields_in_list(300 - find_id_in_list(cid, "championId", match["participants"])["teamId"], "teamId", match["participants"])]),
							"Total CS": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["totalMinionsKilled"] + find_id_in_list(cid, "championId", match["participants"])["stats"]["neutralMinionsKilled"],
							"Total CS diff @20": get_csd20,
							"Dmg to champs": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["totalDamageDealtToChampions"],
							"Dmg dealt": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["totalDamageDealt"],
							"Dmg taken": lambda match, cid: find_id_in_list(cid, "championId", match["participants"])["stats"]["totalDamageTaken"]
							}
STAT_CALCULATION_METHODS = {"Presence": lambda stats: stats["Num Games"] + stats["Bans"],
							"Win %": lambda stats: round(float(stats["Wins"])/max(stats["Num Games"],1),2),
							"Kill Partic": lambda stats: round(float(stats["Kills"] + stats["Assists"])/max(stats["Team Kills"],1),2),
							"Kill Share": lambda stats: round(float(stats["Kills"])/max(stats["Team Kills"],1),2),
							"Death Share": lambda stats: round(float(stats["Deaths"])/max(stats["Enemy Kills"],1),2),
							"Kills/game": lambda stats: round(float(stats["Kills"])/max(stats["Num Games"],1),2),
							"Deaths/game": lambda stats: round(float(stats["Deaths"])/max(stats["Num Games"],1),2),
							"Assists/game": lambda stats: round(float(stats["Assists"])/max(stats["Num Games"],1),2),
							"Avg CS": lambda stats: round(float(stats["Total CS"])/max(stats["Num Games"],1),2),
							"CS per min": lambda stats: round(float(stats["Total CS"])/max(stats["Total gametime"] * 60,1),2),
							"Avg CSD@20": lambda stats: round(float(stats["Total CS diff @20"])/max(stats["Num Games"],1),2),
							"Dmg to champs per game": lambda stats: round(float(stats["Dmg to champs"])/max(stats["Num Games"],1)),
							"Dmg dealt per game": lambda stats: round(float(stats["Dmg dealt"])/max(stats["Num Games"],1)),
							"Dmg taken per game": lambda stats: round(float(stats["Dmg taken"])/max(stats["Num Games"],1))
							}


TEAM_MEMBER_NAMES = ["Däddy Kun", "Shrek Wazowski", "Kadorr", "BigBrainTim", "Rosin", "Feãr", "Áz1r", "sallaD", "Gezang"]
TEAM_MEMBER_ROLES = [("TOP", None), ("TOP", None), ("JUNGLE", None), ("JUNGLE", None), ("JUNGLE", None), ("MIDDLE", None), ("MIDDLE", None), ("BOTTOM", "DUO_CARRY"), ("BOTTOM", "DUO_SUPPORT")]
ALL_ROLES = [("TOP", None), ("JUNGLE", None), ("MIDDLE", None), ("BOTTOM", "DUO_CARRY"), ("BOTTOM", "DUO_SUPPORT")]