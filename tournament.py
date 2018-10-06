import requests
import json
import helpers
import sys
import time
import os
from db_access import fetch_api_key
T_BASE = "https://americas.api.riotgames.com"
M_BASE = "https://na1.api.riotgames.com"
RISEN_PROVIDER_ID = 1725

def provider():
	endpoint = "/lol/tournament/v3/providers/"
	pregparams = {	"region": "NA",
					"url": "https://www.risenesports.org/"
					}
	api_key = fetch_api_key()
	headers = {"X-Riot-Token": api_key}
	body = {"ProviderRegistrationParameters": pregparams}
	url = T_BASE + endpoint
	r = requests.post(url, headers=headers, json=body)
	return r

def tournament(league, season):
	endpoint = "/lol/tournament/v3/tournaments"
	api_key = fetch_api_key()
	tparams= {	"name": "Risen " + league + " Season " + str(season),
				"providerId": RISEN_PROVIDER_ID
					}
	headers = {"X-Riot-Token": api_key}
	url = T_BASE + endpoint
	r = requests.post(url, headers=headers, json=tparams)
	return r.json()

def tournament_codes(tid, count, metadata={}, allowed_sids=None):
	endpoint = "/lol/tournament/v3/codes" + "?tournamentId=" + str(tid) + "&count=" + str(count)
	tcodeparams = {	"mapType":"SUMMONERS_RIFT",
					"pickType":"TOURNAMENT_DRAFT",
					"spectatorType":"ALL",
					"teamSize":5,
					"metadata": json.dumps(metadata)
					}
	if allowed_sids:
		tcodeparams["allowedSummonerIds"] = allowed_sids
	api_key = fetch_api_key()
	headers = {"X-Riot-Token": api_key}
	url = T_BASE + endpoint
	r = requests.post(url, headers=headers, json=tcodeparams)
	if r.status_code != 200:
		print(r.json())
		return None
	return r.json()

def get_tournament_match(mid, tcode):
	endpoint = "/lol/match/v3/matches/" + str(mid) + "/by-tournament-code/"+str(tcode)
	api_key = fetch_api_key()
	headers = {"X-Riot-Token": api_key}
	url = M_BASE + endpoint
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Failed to get match " + str(mid) + " for tcode " + str(tcode))
		print(r.json())
		return None
	return r.json()


def get_matches_for_tcode(tcode):
	path = ".cache/tournament_matches/" + tcode + ".json"
	try:
		matches = helpers.load_json(path)
	except:
		print("Failed to load path")
		print(path)
	miss = True
	if matches is not None:
		file_creation = os.path.getmtime(path)
		expiry_time = 3600 * 24 * 2
		miss = (matches == [] and time.time() > file_creation + expiry_time)
	if miss:
		print("Waiting due to cache miss")
		sys.stdout.flush()
		time.sleep(2)
		
		endpoint = "/lol/match/v3/matches/by-tournament-code/"+str(tcode)+"/ids"
		api_key = fetch_api_key()
		headers = {"X-Riot-Token": api_key}
		url = M_BASE + endpoint
		r = requests.get(url, headers=headers)
		if r.status_code == 404:
			print("Tcode " + str(tcode) + " does not have any games associated with it.")
			matches = []
			helpers.store_json(matches, path, True)
			return matches
		elif r.status_code == 429:
			print("Hit a retry-after when getting tournament matches. Exiting")
			exit(0)
		elif r.status_code != 200:
			print("Failed to get matches for tcode " + str(tcode))
			print(r)
			return r
		matches = []
		for match_id in r.json():
			match = get_tournament_match(match_id, tcode)
			if match:
				matches.append(match)
		helpers.store_json(matches, path, True)
	return matches