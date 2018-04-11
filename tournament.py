import requests
BASE = "https://na1.api.riotgames.com"

def load_tournament_key():
	keyfile = open("tournament_key.txt")
	return keyfile.readlines()[0].strip()

def mock_provider():
	endpoint = "/lol/tournament/v3/providers/"
	pregparams = {	"region": "NA",
					"url": "http://www.risenesports.org/"
					}
	api_key = load_tournament_key()
	headers = {"X-Riot-Token": api_key}
	body = {"ProviderRegistrationParameters": pregparams}
	url = BASE + endpoint
	r = requests.post(url, headers=headers, json=body)
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