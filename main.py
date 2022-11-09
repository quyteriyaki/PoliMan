# from src.workspace_quickstart import main
from src.workspace import Workspace
from src.PoliBot import PoliBot

import discord
import json as JSON

def main():
  disc_token = ""

  with open("config/tokens/discord_tokens.json", 'r') as file_dc_token:
    disc_token = JSON.load(file_dc_token)["token"]

  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True
  intents.guilds = True

  bot = PoliBot(command_prefix="+", intents=intents)
  bot.run(token=disc_token)

if __name__ == "__main__":
  main()