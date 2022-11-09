import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Sheets_API():
  '''Library of functions that perform basic interactions with Google Sheets API'''
  @staticmethod
  def _authenticate(config: dict) -> Credentials:
    creds = None
    if os.path.exists(f"config/servers/{config['guild']}/{config['source']['token']}"):
      creds = Credentials.from_authorized_user_file(f"config/servers/{config['guild']}/{config['source']['token']}", config['source']['scopes'])
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(f"config/servers/{config['guild']}/{config['source']['creds']}", config['source']['scopes'])
        creds = flow.run_console(port=0)
    
    with open(f"config/servers/{config['guild']}/{config['source']['token']}", 'w') as file:
      file.write(creds.to_json())

    return creds

  @staticmethod
  def _getSheet(config: dict):
    creds = Sheets_API._authenticate(config)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()
  
  @staticmethod
  def Query(config: dict, sheet: str, range: str):
    src = Sheets_API._getSheet(config)
    try:
      result = src.values().get(
        spreadsheetId=config['source']['id'],
        range=sheet+"!"+range
      ).execute()

      return result.get('values', [])
    except HttpError as error:
      print(error)
      return error

  @staticmethod
  def Write(config: dict, sheet: str, range: str, data: any):
    src = Sheets_API._getSheet(config)
    try:
      body = {'values': data}
      result = src.values().update(
        spreadsheetId=config['source']['id'],
        range=sheet+"!"+range,
        valueInputOption="USER_ENTERED",
        body = body
      ).execute()

      print(f"{result.get('updatedCells')} cells updated.")
      return result
    except HttpError as error:
      print(error)
      return error