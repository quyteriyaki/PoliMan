# from src.workspace_quickstart import main
from src.workspace import Workspace
from src.PoliBot import PoliBot

import discord
import json as JSON

def main():
  configs = {}
  paths = {}
  disc_token = ""

  with open("config/config.json", 'r') as file:
    configs = JSON.load(file)

  with open("config/paths.json", 'r') as file:
    paths = JSON.load(file)

  with open(paths["discord"]["token"], 'r') as file_dc_token:
    disc_token = JSON.load(file_dc_token)["token"]

  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True

  w = Workspace(paths["workspace"], configs["workspace"])
  w.Initialize(configs["workspace"]["spreadsheet_id"])

  bot = PoliBot(command_prefix="+", intents=intents, workspace=w)
  bot.PassConfigs(paths, configs) 
  bot.run(token=disc_token)

if __name__ == "__main__":
  main()