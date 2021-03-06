import pymysql
from os.path import isfile
import json
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

def fetch_api_key():
	db = pymysql.connect(IP, DB_USER, load_db_password(), WEBSITE_DB)
	cursor = db.cursor()
	query = "SELECT `Key Value` FROM API_ACCESS_KEYS WHERE `API NAME` = 'Riot Tournament API'"
	cursor.execute(query)
	row = cursor.fetchall()[0]
	db.close()
	return row[0]


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

def upload_tcodes(metadata, codes, game=None):
	bteam = metadata["Team1"]
	rteam = metadata["Team2"]
	season = metadata["Season"]
	week = metadata["Week"]
	league = metadata["League"]


	if not game:
		# init values with basic info for row and (required) first code
		values = [league, str(season), str(week), bteam, rteam, codes[0]]
		# append all remaining codes (so bo1 vs bo3 vs bo5 can all be uploaded)
		for i in range(1,len(codes)):
			values.append(codes[i])
		values += [None] * (10 - len(values))
		for i in range(len(values)):
			values[i] = "'" + str(values[i]) + "'"
		query = "INSERT INTO TournamentCodes (League, Season, Week, Team1, Team2, code1, code2, code3, code4, code5) VALUES (" + ",".join(values) + ");"
	else:
		codecolumn = "code" + str(game)
		conditions = "League = '{!s}' AND Season = {!s} AND Week = {!s} AND Team1 = '{!s}' AND Team2 = '{!s}'".format(league, season, week, bteam, rteam)
		query = "UPDATE TournamentCodes SET " + codecolumn + " = '" + str(codes[0]) + "' WHERE " + conditions

	db = pymysql.connect(IP, DB_USER, load_db_password(), WEBSITE_DB)
	cursor = db.cursor()
	cursor.execute(query)
	db.close()

def get_unformatted_tcodes(league, week, team):
	db = pymysql.connect(IP, DB_USER, load_db_password(), WEBSITE_DB)
	cursor = db.cursor()
	query = "SELECT code1,code2,code3,code4,code5 FROM TournamentCodes WHERE League = '{!s}'".format(league)
	query += " AND Week = {!s}".format(str(week))
	query += " AND (Team1 = '{!s}' OR Team2 = '{!s}')".format(team,team)
	cursor.execute(query)
	vals = cursor.fetchall()
	db.close()
	codes = []
	for row in vals:
		codes.extend([v for v in row if v != None])
	return codes

def get_formatted_tcodes(league, week, team=None):
	rtn_str = "Week " + str(week) + ":\n"
	db = pymysql.connect(IP, DB_USER, load_db_password(), WEBSITE_DB)
	cursor = db.cursor()
	query = "SELECT * FROM TournamentCodes WHERE League = '{!s}'".format(league)
	query += " AND Week = {!s}".format(str(week))
	if team:
		query += " AND (Team1 = '{!s}' OR Team2 = '{!s}')".format(team,team)
	cursor.execute(query)
	vals = cursor.fetchall()
	db.close()
	for val in vals:
		rtn_str += val[2] + " vs " + val[3] + ":\n" + "\n".join(val[4:7]) + "\n" + "\n".join([v for v in val[8:] if v is not None and v != "None"]) + "\n"
	return rtn_str

def get_match_history_links(league, week, team):
	from tournament import get_matches_for_tcode
	codes = get_unformatted_tcodes(league, week, team)
	linkbase = "https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/"
	linksuffix = "?tab=overview"
	links = []
	print("codes are")
	print(codes)
	for code in codes:
		if not code or code == "None":
			continue
		matches = get_matches_for_tcode(code)
		if matches:
			for m in matches:
				pid = m["participantIdentities"][0]["player"]["summonerId"]
				link = linkbase + str(m["gameId"]) + "/" + str(pid) + linksuffix
				links.append(link)
	return links

def execute_query(query, db=WEBSITE_DB):
	db = pymysql.connect(IP, DB_USER, load_db_password(), db)
	cursor = db.cursor()
	cursor.execute(query)
	result = cursor.fetchall()
	db.close()
	return result


def main():
	print(get_formatted_tcodes("Rampage", 5))

if __name__ == '__main__':
	# main()
	print(fetch_api_key())
