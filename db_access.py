import pymysql
IP = "50.62.176.249"
DB_USER = "StatisticsTeam"
SCHEMA_DB = "information_schema"
WEBSITE_DB = "RisenWebsite"
TABLES = ["LeagueTypes", "Leagues", "Players", "Teams", "Testing"]
with open("db_pass.txt") as f:
	PASSWORD = f.readlines()[0].strip()

db = pymysql.connect(IP, DB_USER, PASSWORD, WEBSITE_DB)

cursor = db.cursor()

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

cursor.execute(create_test_table_query())
db.close()