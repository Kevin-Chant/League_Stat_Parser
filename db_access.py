import pymysql
IP = "50.62.176.249"
DB_USER = "StatisticsTeam"
SCHEMA_DB = "information_schema"
WEBSITE_DB = "RisenWebsite"
TABLES = ["LeagueTypes", "Leagues", "Players", "Teams"]
with open("db_pass.txt") as f:
	PASSWORD = f.readlines()[0].strip()

db = pymysql.connect(IP, DB_USER, PASSWORD, WEBSITE_DB)

cursor = db.cursor()

cursor.execute("SELECT * FROM LeagueTypes LIMIT 5")
data = cursor.fetchall()
print(str(data))
db.close()