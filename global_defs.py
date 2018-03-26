from collections import OrderedDict
from riot_api_access import *
from stats import *

PLAYER_STATS_SPREADSHEET_ID = "1fu8T513ZZhWDn0Fimc01evXSW6lwxUJI49gHq_BUow8"
STATS_TESTING_SPREADSHEET_ID = "1haqC4FS0pY2bVe9agDLDi5KtMvk4hzRlcl9RvI-We4s"
CUSTOM_TEAM_BG_COLOR = {"red": "183", "green": "225", "blue": "205"}

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
#TODO: fix damage breakdown hierarchy
m = load_json("example_match.json")
p_id = get_partic_id_from_name(m, "Gezang")
stats = get_all_player_stats(m, p_id)
PLAYER_STATS_COL_TITLES = list(stats)
PLAYER_STATS_COL_TITLES.sort()
PLAYER_STATS_COL_TITLES.remove("Player")
PLAYER_STATS_COL_TITLES.insert(0, "Player")


def combine_players(x,y):
	if x["Player"] == y["Player"]:
		return x["Player"]
	else:
		raise ValueError("Aggregating stats from two players")

OVERALL_STATS = ["Player", "Number of games", "Time played", "Kills", "Deaths", "Assists", "KDA", "Kill Participation", "Kill Share", "Death Share", "Team Kills", "Enemy Kills", "Largest MultiKill", "Longest Killing Spree", "Total CS", "CS d@20", "CS per min", "Dmg dealt to champions", "Dmg dealt", "Dmg taken", "Vision Score", "Vision score diff", "Control wards purchased", "Wards Placed"]
OVERALL_STAT_AGG_FUNCS = { 	"Player": lambda x,y: combine_players,
							"Number of games": lambda x,y: x["Number of games"] + y["Number of games"],
							"Time played": lambda x,y: x["Time played"] + y["Time played"],
							"Kills": lambda x,y: x["Kills"] + y["Kills"],
							"Deaths": lambda x,y: x["Deaths"] + y["Deaths"],
							"Assists": lambda x,y: x["Assists"] + y["Assists"],
							"KDA": lambda x,y: round(float(x["Kills"]+x["Assists"]+y["Kills"]+y["Assists"])/(x["Deaths"]+y["Deaths"]),2),
							"Kill Participation": lambda x,y: round(float(x["Kills"]+x["Assists"]+y["Kills"]+y["Assists"])/(x["Team Kills"]+y["Team Kills"]),2),
							"Kill Share": lambda x,y: round(float(x["Kills"]+y["Kills"])/(x["Team Kills"]+y["Team Kills"]),2),
							"Death Share": lambda x,y: round(float(x["Deaths"]+y["Deaths"])/(x["Enemy Kills"]+y["Enemy Kills"]),2),
							"Team Kills": lambda x,y: x["Team Kills"] + y["Team Kills"],
							"Enemy Kills": lambda x,y: x["Enemy Kills"] + y["Enemy Kills"],
							"Largest MultiKill": lambda x,y: max(x["Largest MultiKill"], y["Largest MultiKill"]),
							"Longest Killing Spree": lambda x,y: max(x["Longest Killing Spree"], y["Longest Killing Spree"]),
							"Total CS": lambda x,y: x["Total CS"] + y["Total CS"],
							"CS d@20": lambda x,y: round(float(x["CS d@20"] * x["Number of games"] + y["CS d@20"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"CS per min":lambda x,y: round(float(x["CS per min"] * x["Time played"] + y["CS per min"] * y["Time played"])/(x["Time played"] + y["Time played"]), 2),
							"Dmg dealt to champions": lambda x,y: x["Dmg dealt to champions"] + y["Dmg dealt to champions"],
							"Dmg dealt": lambda x,y: x["Dmg dealt"] + y["Dmg dealt"],
							"Dmg taken": lambda x,y: x["Dmg taken"] + y["Dmg taken"],
							"Vision Score": lambda x,y: round(float(x["Vision Score"] * x["Number of games"] + y["Vision Score"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"Vision score diff": lambda x,y: round(float(x["Vision score diff"] * x["Number of games"] + y["Vision score diff"] * y["Number of games"])/(x["Number of games"] + y["Number of games"]), 2),
							"Control wards purchased": lambda x,y: x["Control wards purchased"] + y["Control wards purchased"],
							"Wards Placed": lambda x,y: x["Wards Placed"] + y["Wards Placed"]
							}