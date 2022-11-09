import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Workspace():
  @staticmethod
  def Authenticate(config: dict) -> Credentials:
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
  def GetSheet(config):
    creds = Workspace.Authenticate(config)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()
  
  @staticmethod
  def Query(config, sheet, range):
    sheet = Workspace.GetSheet(config)
    try:
      result = sheet.values().get(
        spreadsheetId=config['source']['id'],
        range=sheet+"!"+range
      ).execute()

      return result.get('values', [])
    except HttpError as error:
      print(error)
      return error

  @staticmethod
  def Write(config, sheet, range, data):
    sheet = Workspace.GetSheet(config)
    try:
      body = {'values': data}
      result = sheet.values().update(
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