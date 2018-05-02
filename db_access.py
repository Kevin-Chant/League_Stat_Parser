import pymysql
from os.path import isfile
IP = "50.62.176.249"
DB_USER = "StatisticsTeam"
SCHEMA_DB = "information_schema"
WEBSITE_DB = "RisenWebsite"
TABLES = ["LeagueTypes", "Leagues", "Players", "Teams", "Testing", "TournamentCodes", "Tcodetesting"]

def load_db_password():
	if isfile("db_pass.txt"):
		with open("db_pass.txt") as f:
			return f.readlines()[0].strip()


# General format:
# db = pymysql.connect(IP, DB_USER, PASSWORD, WEBSITE_DB)
# cursor = db.cursor()
# cursor.execute("Query string")
# db.close()

def create_test_table_query():
	columnnames = ['PlayerID', 'MatchID', 'TeamID', 'assists', 'champLevel', 'damageDealtToObjectives', 'damageDealtToTurrets', 'damageSelfMitigated', 'deaths', 'doubleKills', 'firstBloodAssist', 'firstBloodKill', 'firstTowerAssist', 'firstTowerKill', 'goldEarned', 'inhibitorKills', 'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'kills', 'largestKillingSpree', 'longestTimeSpentLiving', 'neutralMinionsKilled', 'neutralMinionsKilledEnemyJungle', 'neutralMinionsKilledTeamJungle', 'participantId', 'pentaKills', 'perk0', 'perk0Var1', 'perk0Var2', 'perk0Var3', 'perk1', 'perk1Var1', 'perk1Var2', 'perk1Var3', 'perk2', 'perk2Var1', 'perk2Var2', 'perk2Var3', 'perk3', 'perk3Var1', 'perk3Var2', 'perk3Var3', 'perk4', 'perk4Var1', 'perk4Var2', 'perk4Var3', 'perk5', 'perk5Var1', 'perk5Var2', 'perk5Var3', 'perkPrimaryStyle', 'perkSubStyle', 'quadraKills', 'timeCCingOthers', 'totalDamageDealt', 'totalDamageDealtToChampions', 'totalDamageTaken', 'totalHeal', 'totalMinionsKilled', 'totalTimeCrowdControlDealt', 'tripleKills', 'turretKills', 'visionScore', 'visionWardsBoughtInGame', 'wardsKilled', 'wardsPlaced', 'win']
	columntypes = ["int"] * len(columnnames)
	columnnames += ["lane", "role"]
	columntypes += ["varchar(255)"]*2
	query = "CREATE TABLE Testing ("
	for i in range(len(columnnames)):
		query += columnnames[i] + " " + columntypes[i] + ","
	query += "PRIMARY KEY(PlayerId, MatchID, TeamID));"
	return query

def upload_tcodes(metadata, codes):
	bteam = metadata["Team1"]
	rteam = metadata["Team2"]
	season = metadata["Season"]
	week = metadata["Week"]
	league = metadata["League"]

	values = [league, str(season), str(week), bteam, rteam, codes[0], codes[1], codes[2]]
	for i in range(len(values)):
		values[i] = "'" + values[i] + "'"
	
	db = pymysql.connect(IP, DB_USER, load_db_password(), WEBSITE_DB)
	cursor = db.cursor()
	cursor.execute("INSERT INTO TournamentCodes (League, Season, Week, Team1, Team2, code1, code2, code3) VALUES (" + ",".join(values) + ");")
	db.close()
