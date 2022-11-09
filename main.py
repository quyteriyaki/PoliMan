from src.PoliBot import PoliBot

import discord
import json

def main():
  disc_token = ""

  with open("config/tokens/discord_tokens.json", 'r') as file_dc_token:
    disc_token = json.load(file_dc_token)["token"]

  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True
  intents.guilds = True

  bot = PoliBot(command_prefix="+", intents=intents)
  bot.run(token=disc_token)

if __name__ == "__main__":
  main()