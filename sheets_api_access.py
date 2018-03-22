import httplib2
import os
from collections import OrderedDict
from stats import *

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/spreadsheets"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Google Sheets API Python Quickstart"

PLAYER_STATS_SPREADSHEET_ID = "1fu8T513ZZhWDn0Fimc01evXSW6lwxUJI49gHq_BUow8"
STATS_TESTING_SPREADSHEET_ID = "1haqC4FS0pY2bVe9agDLDi5KtMvk4hzRlcl9RvI-We4s"
CUSTOM_TEAM_BG_COLOR = {"red": "183", "green": "225", "blue": "205"}

PLAYER_STATS_KEY_HIERARCHY = OrderedDict([  ("Combat Stats", ["Kills", "Deaths", "Assists", "KDA", "Kill Participation", "Kill Share", "Team Kills", "Enemy Kills", "Death Share", "Largest MultiKill", "Longest Killing Spree"]),
                                            ("Damage Stats", ["Objective Damage", "Turret Damage", "Total CC duration", "Dmg taken per min by min", "Dmg taken diff per min by min", "Heals Given", "Damage type breakdown"]),
                                            ("Vision Stats", OrderedDict([  ("Player", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Opponent", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Absolute Difference", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"]),
                                                                            ("Relative Score", ["Wards placed", "Control wards purchased", "Wards killed", "Vision score"])
                                                    ])
                                            ),
                                            ("CS stats", ["Total CS", "CS per min", "CS per min by min", "CS differential", "CS differential by min"])
                                ])
#TODO: fix damage breakdown hierarchy
m = load_json("example_match.json")
p_id = get_partic_id_from_name(m, "Gezang")
stats = get_all_player_stats(m, p_id)
PLAYER_STATS_COL_TITLES = list(stats)
PLAYER_STATS_COL_TITLES.sort()
PLAYER_STATS_COL_TITLES.remove("Player")
PLAYER_STATS_COL_TITLES.insert(0, "Player")



def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   "sheets.googleapis.com-python-quickstart.json")

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print("Storing credentials to " + credential_path)
    return credentials

def credential_service_setup():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ("https://sheets.googleapis.com/$discovery/rest?"
                    "version=v4")
    service = discovery.build("sheets", "v4", http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service

def create_sheet(spreadsheetId, sheetId, service=None):
    if not service:
        service = credential_service_setup()
    properties = {
        "title": sheetId,
    }
    requests = [{"addSheet": {"properties": properties}}]
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={"requests": requests})
    response = request.execute()
    print(response)

def create_sheets(spreadsheetId, sheetIds, service=None):
    if not service:
        service = credential_service_setup()
    requests = []
    for sheetId in sheetIds:
        requests.append({
                            "addSheet": {
                                        "properties": {
                                                        "title": sheetId
                                                       }
                                        }
                        })
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={"requests": requests})
    response = request.execute()
    print(response)

def get_numeric_sheetId(spreadsheetId, sheetId, service=None):
    if not service:
        service = credential_service_setup()
    request = service.spreadsheets().get(spreadsheetId=spreadsheetId, fields="sheets.properties")
    response = request.execute()
    title_dict = {sheet["properties"]["title"] : sheet["properties"]["sheetId"] for sheet in response["sheets"]}
    if not sheetId in title_dict:
        return None
    else:
        return title_dict[sheetId]

def setup_player_stat_sheet(spreadsheetId, sheetId, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    data = [
        {
            "range":sheetId+"!A1:AAA1",
            "majorDimension":"ROWS",
            "values":[PLAYER_STATS_COL_TITLES]
        }
        ]

    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={"valueInputOption": "USER_ENTERED", "data": data})
    response = request.execute()
    return response

def format_player_stat_sheet(spreadsheetId, sheetId, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    requests = [
    {
      "autoResizeDimensions": {
        "dimensions": {
          "sheetId": numeric_sheetId,
          "dimension": "COLUMNS",
          "startIndex": 0,
          "endIndex": len(PLAYER_STATS_COL_TITLES)+1
        }
      }
    }
    ]
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={"requests": requests})
    response = request.execute()
    return response

def enter_player_stat_row(spreadsheetId, sheetId, row, stats, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    data = [
        {
            "range":sheetId+"!A" + str(row) + ":BK" + str(row),
            "majorDimension":"ROWS",
            "values":[stats]
        }
        ]

    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={"valueInputOption": "USER_ENTERED", "data": data})
    response = request.execute()
    return response

def read_existing_stats(spreadsheetId, sheetId, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    rang = sheetId + "!A2:BK"
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rang)
    response = request.execute()
    return response


if __name__ == "__main__":
    sheetId="All Players"
    service = credential_service_setup()
    if not get_numeric_sheetId(PLAYER_STATS_SPREADSHEET_ID, sheetId, service):
        create_sheet(PLAYER_STATS_SPREADSHEET_ID, sheetId, service)
    r = setup_player_stat_sheet(PLAYER_STATS_SPREADSHEET_ID, sheetId, service)
    r2 = format_player_stat_sheet(PLAYER_STATS_SPREADSHEET_ID, sheetId, service)
    to_write = [stats[key] for key in PLAYER_STATS_COL_TITLES]
    r3 = enter_player_stat_row(PLAYER_STATS_SPREADSHEET_ID, sheetId, 2, to_write, service)
    r4 = read_existing_stats(PLAYER_STATS_SPREADSHEET_ID, sheetId, service)