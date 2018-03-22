import requests
import sys
BASE = "https://na1.api.riotgames.com"

def read_api_key():
	keyfile = open("riot_secret.txt")
	return keyfile.readlines()[0].strip()

def get_champion_id_dict(SECRET_API_KEY=None):
	if not SECRET_API_KEY:
		SECRET_API_KEY = read_api_key()
	url = BASE + "/lol/static-data/v3/champions?locale=en_US&dataById=true"
	headers = {"X-Riot-Token": SECRET_API_KEY}
	r = requests.get(url,headers=headers)
	if r.status_code != 200:
		print("Get champion id dict failed")
		return r
	dct = {}
	data = r.json()["data"]
	for champ_id in data:
		dct[champ_id] = data[champ_id]["name"]
	return dct

def get_account_id(summoner_name, SECRET_API_KEY=None):
	if not SECRET_API_KEY:
		SECRET_API_KEY = read_api_key()
	if not summoner_name:
		raise TypeError("Summoner name cannot be None")
	if not isinstance(summoner_name, str):
		raise TypeError("Summoner name must be a string")
	url = BASE + "/lol/summoner/v3/summoners/by-name/" + summoner_name
	headers = {"X-Riot-Token": SECRET_API_KEY}
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Get account id failed")
		return r
	response = r.json()
	if "name" not in response:
		print("No such name exists")
		return response
	return response["accountId"]

def get_recent_history(accountid, SECRET_API_KEY=None):
	if not SECRET_API_KEY:
		SECRET_API_KEY = read_api_key()
	if not accountid:
		raise TypeError("Account id cannot be None")
	if not isinstance(accountid, int):
		raise TypeError("Account id must be an int")
	url = BASE + "/lol/match/v3/matchlists/by-account/" + str(accountid) +  "/recent"
	headers = {"X-Riot-Token": SECRET_API_KEY}
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Get match history failed")
		return r
	response = r.json()
	if "matches" not in response:
		print("Idk what happened but theres no match history")
		return response
	return response["matches"]

def get_match_from_id(matchid, SECRET_API_KEY=None):
	if not SECRET_API_KEY:
		SECRET_API_KEY = read_api_key()
	if not matchid:
		raise TypeError("Match id cannot be None")
	if not isinstance(matchid, int):
		raise TypeError("Match id must be an int")
	url = BASE + "/lol/match/v3/matches/" + str(matchid)
	headers = {"X-Riot-Token": SECRET_API_KEY}
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Get match object failed")
		return r
	return r.json()