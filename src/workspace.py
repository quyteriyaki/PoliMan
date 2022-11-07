import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Workspace():
  def __init__(self, paths = {}, workspace_configs = {}):
    creds = None
    if os.path.exists(paths["token"]):
      creds = Credentials.from_authorized_user_file(paths["token"], workspace_configs["scopes"])
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(paths["creds"], workspace_configs["scopes"])
        creds = flow.run_local_server(port=0)
    

    with open(paths["token"], 'w') as token:
      token.write(creds.to_json())

    self.service = build('sheets', 'v4', credentials=creds)
    self.sheet = self.service.spreadsheets()
  
  def Initialize(self, sheetID: str):
    self.src = sheetID
  
  def Query(self, sheet, range):
    try:
      result = self.sheet.values().get(
        spreadsheetId=self.src, range=sheet+"!"+range).execute()

      rows = result.get('values', [])
      return rows
    except HttpError as error:
      print(error)
      return error
  
  def BatchQuery(self, sheet, ranges):
    try:
      result = self.sheet.values().batchGet(
        spreadsheetId=self.src, ranges=sheet+"!"+ranges).execute()

      return result.get('values', [])
    except HttpError as error:
      print(error)
      return error

  def Write(self, sheet, range, data):
    try:
      body = {
        'values': data
      }
      result = self.sheet.values().update(spreadsheetId=self.src, range=sheet+"!"+range, valueInputOption="USER_ENTERED", body = body).execute()
      print(f"{result.get('updatedCells')} cells updated.")
      return result
    except HttpError as error:
      print(error)
      return error