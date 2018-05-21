import requests
import json
T_BASE = "https://americas.api.riotgames.com"
M_BASE = "https://na1.api.riotgames.com"
RISEN_PROVIDER_ID = 1583

def load_tournament_key():
	keyfile = open("tournament_key.txt")
	return keyfile.readlines()[0].strip()

def provider():
	endpoint = "/lol/tournament/v3/providers/"
	pregparams = {	"region": "NA",
					"url": "https://www.risenesports.org/"
					}
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	body = {"ProviderRegistrationParameters": pregparams}
	url = T_BASE + endpoint
	r = requests.post(url, headers=headers, json=body)
	return r

def tournament(league, season):
	endpoint = "/lol/tournament/v3/tournaments"
	api_key = load_tournament_key()
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
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	url = T_BASE + endpoint
	r = requests.post(url, headers=headers, json=tcodeparams)
	if r.status_code != 200:
		print(r.json())
		return None
	return r.json()

def get_tournament_match(mid, tcode):
	endpoint = "/lol/match/v3/matches/" + str(mid) + "/by-tournament-code/"+str(tcode)
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	url = M_BASE + endpoint
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Failed to get match " + str(mid) + " for tcode " + str(tcode))
		return r
	return r.json()


def get_matches_for_tcode(tcode):
	endpoint = "/lol/match/v3/matches/by-tournament-code/"+str(tcode)+"/ids"
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	url = M_BASE + endpoint
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Failed to get matches for tcode " + str(tcode))
		return r
	matches = []
	for match_id in r.json():
		matches.append(get_tournament_match(match_id, tcode))
	return matches