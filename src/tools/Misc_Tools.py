import discord
import json
import os

def GetGuildConfig(guild: discord.Guild) -> dict:
  path = f"config/servers/{guild.id}"
  if os.path.exists(path):
    with open(path + "config.json", 'r') as file:
      return json.load(file)
  return None

def WriteGuildConfig(guild: discord.Guild, config) -> dict:
  path = f"config/servers/{guild.id}"
  if os.path.exists(path):
    with open(path + "config.json", 'w') as file:
      file.write(json.dumps(config))
      return True
  return False