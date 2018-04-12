import requests
BASE = "https://americas.api.riotgames.com"

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
	url = BASE + endpoint
	r = requests.post(url, headers=headers, json=body)
	return r

pid = 1567

def tournament():
	endpoint = "/lol/tournament/v3/tournaments"
	api_key = load_tournament_key()
	tparams= {"name": "Risen Test Tournament",
  	"providerId": pid
	}
	headers = {"X-Riot-Token": api_key}
	body={"TournamentRegistrationParameters": tparams}
	url = BASE + endpoint
	r = requests.post(url, headers=headers, json=tparams)
	return r

def mock_tournament_codes(tid, allowed_sids=None, numcodes=None):
	endpoint = "/lol/tournament-stub/v3/codes"
	tcodeparams = {	"mapType":"SUMMONERS_RIFT",
					"pickType":"TOURNAMENT_DRAFT",
					"spectatorType":"ALL",
					"teamSize":5
					}
	if allowed_sids:
		tcodeparams["allowedSummonerIds"] = allowed_sids
	api_key = load_tournament_key()
	headers = { "X-Riot-Token": api_key,
				"tournamentId": tid,
				}
	body = {"TournamentCodeParameters": tcodeparams}
	r = requests.post(url, headers=headers, json=body)
	return r

def get_tournament_match(mid, tcode):
	endpoint = "/lol/tournament/v3/matches/" + str(mid) + "/by-tournament-code/"+str(tcode)
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	url = BASE + endpoint
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Failed to get match " + str(mid) + " for tcode " + str(tcode))
		return r
	return r.json()


def get_matches_for_tcode(tcode):
	endpoint = "/lol/tournament/v3/matches/by-tournament-code/"+str(tcode)+"/ids"
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	url = BASE + endpoint
	r = requests.get(url, headers=headers)
	if r.status_code != 200:
		print("Failed to get matches for tcode " + str(tcode))
		return r
	matches = []
	for match_id in r.json():
		matches.append(get_tournament_match(match_id, tcode))
	return matches