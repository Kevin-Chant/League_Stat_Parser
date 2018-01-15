from __future__ import print_function
import httplib2
import os

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
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

OFFICIAL_MATCH_HISTORY_SHEET_ID = '1AGwem7h-yu2Ddell7TAmJsc9B7iOAy_TMvqmAwdXuSM'
CUSTOM_TEAM_BG_COLOR = {'red': '183', 'green': '225', 'blue': '205'}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def credential_service_setup():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service

def create_sheet(spreadsheetId, sheetId):
    service = credential_service_setup()
    properties = {
        'title': sheetId,
    }
    requests = [{'addSheet': {'properties': properties}}]
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={'requests': requests})
    response = request.execute()
    print(response)

def create_sheets(spreadsheetId, sheetIds):
    service = credential_service_setup()
    requests = []
    for sheetId in sheetIds:
        requests.append({
                            'addSheet': {
                                        'properties': {
                                                        'title': sheetId
                                                       }
                                        }
                        })
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={'requests': requests})
    response = request.execute()
    print(response)

def get_numeric_sheetId(spreadsheetId, sheetId):
    service = credential_service_setup()
    request = service.spreadsheets().get(spreadsheetId=spreadsheetId, fields='sheets.properties')
    response = request.execute()
    title_dict = {sheet['properties']['title'] : sheet['properties']['sheetId'] for sheet in response['sheets']}
    if not sheetId in title_dict:
        return None
    else:
        return title_dict[sheetId]

def sheet_setup(spreadsheetId, sheetId):
    numeric_sheetId = get_numeric_sheetId(OFFICIAL_MATCH_HISTORY_SHEET_ID, sheetId)
    if not numeric_sheetId:
        print("Error: Could not find sheet " + sheetId)
        return
    service = credential_service_setup()
    requests = []

    # Color team names
    requests.append({'repeatCell': {'range': {'sheetId': numeric_sheetId, 'startRowIndex': '0', 'startColumnIndex': '0', 'endRowIndex': '1', 'endColumnIndex': '1'}, 'cell': {'userEnteredFormat': {'backgroundColor': CUSTOM_TEAM_BG_COLOR}}}})

    # Write a test
    data = [
        {
            'range':'test!A1:A1',
            'majorDimension':'ROWS',
            'values':[['Testing title']]
        }
        ]


    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={'valueInputOption': 'USER_ENTERED', 'data': data, 'requests': requests})
    response = request.execute()
    print(response)

if __name__ == '__main__':
    sheetId='test'
    if not get_numeric_sheetId(OFFICIAL_MATCH_HISTORY_SHEET_ID, sheetId):
        create_sheet(OFFICIAL_MATCH_HISTORY_SHEET_ID, sheetId)
    sheet_setup(OFFICIAL_MATCH_HISTORY_SHEET_ID, sheetId)