import httplib2
import os
import datetime
from collections import OrderedDict
from helpers import *
from stats import *
from champion_stats import *
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


def enter_row(spreadsheetId, sheetId, row, to_enter, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    data = [
        {
            "range":sheetId+"!A" + str(row) + ":AAA" + str(row),
            "majorDimension":"ROWS",
            "values":[to_enter]
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

def enter_rows(spreadsheetId, sheetId, row, to_enter, service=None):
    numeric_sheetId = get_numeric_sheetId(spreadsheetId, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    if not service:
        service = credential_service_setup()
    data = [
        {
            "range":sheetId+"!A" + str(row) + ":BK" + str(row+len(to_enter)),
            "majorDimension":"ROWS",
            "values":to_enter
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

def update_rmt_stats(start_date, service=None):
    if not service:
        service = credential_service_setup()
    sheetId="Recent Player Stats"
    if not get_numeric_sheetId(RMT_STATS_SHEET, sheetId, service):
        create_sheet(RMT_STATS_SHEET, sheetId, service)
    r = enter_rows(RMT_STATS_SHEET, sheetId, 1, [OVERALL_STATS], service)
    r = format_player_stat_sheet(RMT_STATS_SHEET, sheetId, service)
    epoch = date_to_epoch(int(start_date[0]), int(start_date[2:]), 2018)
    to_write = [["Stats since " + start_date]]
    for i in range(len(TEAM_MEMBER_NAMES)):
        print("Getting stats on " + TEAM_MEMBER_NAMES[i])
        sys.stdout.flush()
        stats = get_and_cache_user_history(TEAM_MEMBER_NAMES[i], epoch, None, None, TEAM_MEMBER_ROLES[i])
        stats["Player"] = TEAM_MEMBER_NAMES[i]
        to_write.append([stats[key] for key in OVERALL_STATS])
    print("Writing time")
    to_write.append(["Last updated", str(datetime.date.today())])
    r4 = enter_rows(RMT_STATS_SHEET, sheetId, 2, to_write, service)

    sheetId="Total Player Stats"
    if not get_numeric_sheetId(RMT_STATS_SHEET, sheetId, service):
        create_sheet(RMT_STATS_SHEET, sheetId, service)
    r = enter_rows(RMT_STATS_SHEET, sheetId, 1, [OVERALL_STATS], service)
    r = format_player_stat_sheet(RMT_STATS_SHEET, sheetId, service)
    start_date = "4/1"
    epoch = date_to_epoch(int(start_date[0]), int(start_date[2:]), 2018)
    to_write = []
    for i in range(len(TEAM_MEMBER_NAMES)):
        print("Getting stats on " + TEAM_MEMBER_NAMES[i])
        sys.stdout.flush()
        stats = get_and_cache_user_history(TEAM_MEMBER_NAMES[i], epoch, None, None, TEAM_MEMBER_ROLES[i])
        stats["Player"] = TEAM_MEMBER_NAMES[i]
        to_write.append([stats[key] for key in OVERALL_STATS])
    print("Writing time")
    to_write.append([])
    to_write.append(["Stats since 4/1"])
    to_write.append(["Last updated", str(datetime.date.today())])
    r4 = enter_rows(RMT_STATS_SHEET, sheetId, 2, to_write, service)


if __name__ == "__main__":
    update_rmt_stats("4/26")
    # service = credential_service_setup()
    # sheetId="Champion Stats Test"
    # if not get_numeric_sheetId(STATS_TESTING_SHEET, sheetId, service):
    #     create_sheet(STATS_TESTING_SHEET, sheetId, service)

    # m_obs = [download_match_with_cache(id) for id in [2751554415, 2751933982, 2751934225, 2751934437, 2751934627]]
    # stats = agg_champ_stats(m_obs)
    # r = enter_row(STATS_TESTING_SHEET, sheetId, 1, ["Champion Name"] + TRACKED_CHAMPION_STATS + ON_DEMAND_CHAMPION_STATS, service)
    # i = 2
    # for cid in stats.keys():
    #     ods = calculate_ods(stats[cid])
    #     to_write = [convert_champ_id_to_name(cid)] + [stats[cid][key] for key in TRACKED_CHAMPION_STATS] + [ods[key] for key in ON_DEMAND_CHAMPION_STATS]
    #     enter_row(STATS_TESTING_SHEET, sheetId, i, to_write, service)
    #     i+=1