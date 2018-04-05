import httplib2
import os
import datetime
from collections import OrderedDict
from helpers import *
from stats import *
import sys

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
            "values":[OVERALL_STATS]
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
          "endIndex": len(OVERALL_STATS)
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
    sheetId="Player Stats"
    service = credential_service_setup()
    if not get_numeric_sheetId(STATS_TESTING_SPREADSHEET_ID, sheetId, service):
        create_sheet(STATS_TESTING_SPREADSHEET_ID, sheetId, service)
    r = setup_player_stat_sheet(STATS_TESTING_SPREADSHEET_ID, sheetId, service)
    r = format_player_stat_sheet(STATS_TESTING_SPREADSHEET_ID, sheetId, service)
    r = enter_player_stat_row(STATS_TESTING_SPREADSHEET_ID, sheetId, 2, ["Homework 4/5 thru 4/12"], service)
    for i in range(len(TEAM_MEMBER_NAMES)):
        print("Getting stats on " + TEAM_MEMBER_NAMES[i])
        sys.stdout.flush()
        stats = get_and_cache_user_history(TEAM_MEMBER_NAMES[i], date_to_epoch(4,5,2018), date_to_epoch(), None, TEAM_MEMBER_ROLES[i])
        stats["Player"] = TEAM_MEMBER_NAMES[i]
        to_write = [stats[key] for key in OVERALL_STATS]
        r = enter_player_stat_row(STATS_TESTING_SPREADSHEET_ID, sheetId, i+3, to_write, service)
        print("Writing stats on " + TEAM_MEMBER_NAMES[i])
        sys.stdout.flush()
    print("Writing time")
    to_write = ["Last updated", str(datetime.date.today())]
    r4 = enter_player_stat_row(STATS_TESTING_SPREADSHEET_ID, sheetId, len(TEAM_MEMBER_NAMES)+3, to_write, service)