from discord.ext import commands
from discord import app_commands
import discord
import discord.ui as ui
from src.workspace_utils import *
import json as JSON

class Administration(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command("add_role")
  async def add_role(self, interaction: discord.Interaction, role: discord.Role):
    if "roles" not in self.bot.configs:
      self.bot.configs["roles"] = []

    self.bot.configs["roles"].append(role.id)

    with open("config/config.json", "w") as file:
      JSON.dump(self.bot.configs, file, indent = 4)
  
  
  @commands.command("accept")
  async def accept(self, interaction: discord.Interaction, member: discord.Member, forceRole: discord.Role=None):
    # ! [TODO] Do something about moving wishlist -> member sheet
    # Check if the role exists
    await member.add_roles(forceRole)
    pass