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

PLAYER_STATS_COL_TITLES = [ [""]*18 + ["Damage type breakdown"] + [""] * 11 + ["Vision Stats"] + [""] * 19,
                            [""] + ["Combat Stats"] + [""] * 10 + ["Damage Stats"] + [""] * 5 + ["Dealt"] + [""] * 3 + ["Dealt to Champions"] + [""] * 3 + ["Taken"] + [""] * 3 + ["Player"] + [""] * 3 + ["Opponent"] + [""] * 3 + ["Absolute Difference"] + [""] * 3 + ["Relative Score"] + [""] * 3 + ["CS stats"] + [""] * 3,
                            ["Player", "Kills", "Deaths", "Assists", "KDA", "Kill Participation", "Kill Share", "Team Kills", "Enemy Kills", "Death Share", "Largest MultiKill", "Longest Killing Spree", "Objective Damage", "Turret Damage", "Total CC duration", "Dmg taken per min by min", "Dmg taken diff per min by min", "Heals Given", "Total", "Physical", "Magic", "True", "Total", "Physical", "Magic", "True", "Total", "Physical", "Magic", "True", "Wards placed", "Control wards purchased", "Wards killed", "Vision score", "Wards placed", "Control wards purchased", "Wards killed", "Vision score", "Wards placed", "Control wards purchased", "Wards killed", "Vision score", "Wards placed", "Control wards purchased", "Wards killed", "Vision score", "Total CS", "CS per min", "CS per min by min", "CS differential"]
                            ]


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

def create_sheet(spreadsheetId, sheetId):
    service = credential_service_setup()
    properties = {
        "title": sheetId,
    }
    requests = [{"addSheet": {"properties": properties}}]
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={"requests": requests})
    response = request.execute()
    print(response)

def create_sheets(spreadsheetId, sheetIds):
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

def get_numeric_sheetId(spreadsheetId, sheetId):
    service = credential_service_setup()
    request = service.spreadsheets().get(spreadsheetId=spreadsheetId, fields="sheets.properties")
    response = request.execute()
    title_dict = {sheet["properties"]["title"] : sheet["properties"]["sheetId"] for sheet in response["sheets"]}
    if not sheetId in title_dict:
        return None
    else:
        return title_dict[sheetId]

def setup_player_stat_sheet(spreadsheetId, sheetId):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    service = credential_service_setup()
    # Write a test
    data = [
        {
            "range":sheetId+"!A1:AX3",
            "majorDimension":"ROWS",
            "values":PLAYER_STATS_COL_TITLES
        }
        ]

    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={"valueInputOption": "USER_ENTERED", "data": data})
    response = request.execute()
    return response

if __name__ == "__main__":
    # sheetId="Player Stats"
    # if not get_numeric_sheetId(STATS_TESTING_SPREADSHEET_ID, sheetId):
    #     create_sheet(STATS_TESTING_SPREADSHEET_ID, sheetId)
    # r = setup_player_stat_sheet(STATS_TESTING_SPREADSHEET_ID, sheetId)