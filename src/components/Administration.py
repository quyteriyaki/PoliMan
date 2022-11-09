from discord.ext import commands
from discord import app_commands
import os
import discord
import discord.ui as ui
from src.Sheets_Utils import *
import json
from src.tools.Misc_Tools import *
class Administration(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="setup", description="Set up PoliBot for use")
  async def setup(self, interaction: discord.Interaction, config: str = None):
    if not interaction.permissions.manage_guild:
      # ? MESSAGE: NO AUTH
      await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
      return

    # Check if config file
    if not config:
      # ? MESSAGE: INSTRUCTIONS - CONFIG
      await interaction.response.send_message("For now, you will need to pass a configuration file to set up.\n Please refer to the github link for a template.", ephemeral=True)
      return
    
    # Check if a folder exists
    if os.path.exists(f"config/servers/{interaction.guild_id}"):
      # ? MESSAGE: QUESTION - REPLACE CONFIG
      await interaction.response.send_message("An existing configuration file has been found. Would you like to replace it?", ephemeral=True)
      return

    # If it doesn't exist and we have a config, set it up and go
    # Try to convert
    d_config = {}
    try:
      d_config = json.loads(config)
    except:
      # ? ERROR: INVALID CONFIG
      await interaction.response.send_message("Invalid config file.", ephemeral=True)
      return

    os.makedirs(f"{os.getcwd()}/config/servers/{interaction.guild_id}")
    WriteGuildConfig(interaction.guild, d_config)

    # ? MESSAGE: SUCCESS - CONFIG ADDED
    await interaction.response.send_message("Config successfully added!", ephemeral=True)