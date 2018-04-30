import requests
import sys
import time
import helpers
BASE = "https://na1.api.riotgames.com"
QUEUES = [400, 420, 430, 440]

def read_api_key():
	keyfile = open("riot_secret.txt")
	return keyfile.readlines()[0].strip()

def get_champion_id_dict(SECRET_API_KEY=None):
	dct = helpers.load_json(".cache/champ_ids.json")
	if not dct or time.time() > dct["expiry_time"]:
		if not SECRET_API_KEY:
			SECRET_API_KEY = read_api_key()
		url = BASE + "/lol/static-data/v3/champions?locale=en_US&dataById=true"
		headers = {"X-Riot-Token": SECRET_API_KEY}
		r = requests.get(url,headers=headers)
		if r.status_code == 429:
			print(r.json())
			t = r.json()["Retry-After"]
			print("Waiting " + str(t) + " seconds and trying again")
			print("Full response:")
			print(r.json())
			time.sleep(t)
			return get_match_from_id(matchid, SECRET_API_KEY)
		if r.status_code != 200:
			print("Get champion id dict failed")
			return r
		dct = {}
		data = r.json()["data"]
		for champ_id in data:
			dct[champ_id] = data[champ_id]["name"]
		dct["expiry_time"] = time.time() + 60*60*24*30 # Expires after one month
		if not helpers.store_json(dct, ".cache/champ_ids.json", True):
			return None
		return dct
	else:
		return dct

def get_account_id(summoner_name, SECRET_API_KEY=None):
	dct = helpers.load_json(".cache/summoners/" + summoner_name + ".json")
	if not dct or time.time() > dct["expiry_time"]:
		if not SECRET_API_KEY:
			SECRET_API_KEY = read_api_key()
		if not summoner_name:
			raise TypeError("Summoner name cannot be None")
		if not isinstance(summoner_name, str):
			raise TypeError("Summoner name must be a string")
		url = BASE + "/lol/summoner/v3/summoners/by-name/" + summoner_name
		headers = {"X-Riot-Token": SECRET_API_KEY}
		r = requests.get(url, headers=headers)
		if r.status_code == 429:
			print(r.json())
			t = r.json()["Retry-After"]
			print("Waiting " + str(t) + " seconds and trying again")
			print("Full response:")
			print(r.json())
			time.sleep(t)
			return get_match_from_id(matchid, SECRET_API_KEY)
		if r.status_code != 200:
			print("Get account id failed")
			return r
		response = r.json()
		response["expiry_time"] = time.time() + 60*60*24*30 # Expires after one month
		helpers.store_json(response, ".cache/summoners/" + summoner_name + ".json", True)
		return response["accountId"]
	else:
		return dct["accountId"]

def get_recent_history(accountid, SECRET_API_KEY=None):
	hist = helpers.load_json(".cache/recent_histories/" + str(accountid) + ".json")
	if not hist or time.time() > hist["expiry_time"]:
		if not SECRET_API_KEY:
			SECRET_API_KEY = read_api_key()
		if not accountid:
			raise TypeError("Account id cannot be None")
		if not isinstance(accountid, int):
			raise TypeError("Account id must be an int")
		url = BASE + "/lol/match/v3/matchlists/by-account/" + str(accountid) +  "/recent"
		headers = {"X-Riot-Token": SECRET_API_KEY}
		r = requests.get(url, headers=headers)
		if r.status_code == 429:
			print(r.json())
			t = r.json()["Retry-After"]
			print("Waiting " + str(t) + " seconds and trying again")
			print("Full response:")
			print(r.json())
			time.sleep(t)
			return get_match_from_id(matchid, SECRET_API_KEY)
		if r.status_code != 200:
			print("Get match history failed")
			return r
		response = r.json()
		if "matches" not in response:
			print("There is no recent match history")
			return []
		hist = {"expiry_time": time.time() * 60*60*2,
				"matches": response["matches"]
				}
		helpers.store_json(hist, ".cache/recent_histories/" + str(accountid) + ".json",True) # Expires after 2 hours
		return hist["matches"]
	else:
		return hist["matches"]

def get_match_from_id(matchid, SECRET_API_KEY=None):
	match = helpers.load_json(".match_cache/" + str(matchid) + ".json")
	if not match:
		if not SECRET_API_KEY:
			SECRET_API_KEY = read_api_key()
		if not matchid:
			raise TypeError("Match id cannot be None")
		if not isinstance(matchid, int):
			raise TypeError("Match id must be an int")
		url = BASE + "/lol/match/v3/matches/" + str(matchid)
		headers = {"X-Riot-Token": SECRET_API_KEY}
		r = requests.get(url, headers=headers)
		if r.status_code == 429:
			print("\n"*5)
			print(r.json())
			print("\n"*5)
			t = r.json()["Retry-After"]
			print("Waiting " + str(t) + " seconds and trying again")
			print("Full response:")
			print(r.json())
			time.sleep(t)
			return get_match_from_id(matchid, SECRET_API_KEY)
		if r.status_code != 200:
			print("Get match object failed")
			return r
		match = r.json()
		helpers.store_json(match, ".match_cache/" + str(matchid) + ".json", True)
		return match
	else:
		return match

def get_match_history(accountid, beginTime=None, endTime=None, champions=None, SECRET_API_KEY=None):
	if not SECRET_API_KEY:
		SECRET_API_KEY = read_api_key()
	url = BASE + "/lol/match/v3/matchlists/by-account/" + str(accountid)
	headers = {"X-Riot-Token": SECRET_API_KEY}
	params = {"queue": QUEUES}
	if beginTime: params["beginTime"] = beginTime
	if endTime: params["endTime"] = endTime
	if champions:
		if type(champions[0]) == str:
			for i in range(len(champions)):
				champions[i] = convert_champ_name_to_id(champions[i])
		params["champion"] = champions
	r = requests.get(url, headers=headers, params=params)
	if r.status_code == 429:
		print(r.json())
		t = r.json()["Retry-After"]
		print("Waiting " + str(t) + " seconds and trying again")
		print("Full response:")
		print(r.json())
		time.sleep(t)
		return get_match_from_id(matchid, SECRET_API_KEY)
	if r.status_code == 404:
		print("There is no match history in that time frame")
		return {"matches":[]}
	if r.status_code != 200:
		print("Get match history failed")
		print(r.json())
		return r
	return r.json()