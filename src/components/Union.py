from discord.ext import commands
from discord import app_commands
import discord
import discord.ui as ui
from src.Sheets_Utils import *
from src.Sheets_API import Sheets_API
from src.tools.Misc_Tools import *
from src.tools.Rego_Tools import *

from datetime import datetime

class Union(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # --------------------------------------
  # ! + Spreadsheet Functions
  # --------------------------------------

  def PushToSource(self, guild: discord.Guild, sheet: str, region: str, vals: list, excludeCount: int = 1, rangeFix: tuple = (0, 0)) -> bool:
    '''Adds data at at an empty location within the table'''
    if not self.bot.edit_mode: return True
    config = GetGuildConfig(guild)

    region = config["source"]["regions"][region]

    if config["source"]["type"] == "sheets":
      data = Sheets_API.Query(config, sheet, region)
      rowRange = FindEmptyRow(data, region, excludeCount = excludeCount)

      if not rowRange: return False

      rowRange[0] = mathCell(rowRange[0], rangeFix[0], 0)
      rowRange[1] = mathCell(rowRange[1], rangeFix[1], 0)

      output = Sheets_API.Write(config, sheet, ":".join(rowRange), vals)
      return output.get('updatedCells') != 0

  def addReceiptToWaitlist(self, guild: discord.Guild, receipt) -> bool:
    return self.PushToSource(guild, "Waitlist", "waitlist", 
      [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]], 
      excludeCount=1,
      rangeFix=(1, 0)
    )

  def addToRoster(self, guild: discord.Guild, receipt) -> bool:
    return self.PushToSource(guild, receipt["union"], "members_normal",
      [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"]]],
      excludeCount=3, rangeFix=(1, 4)
    )

  def ReplaceToSource(self, guild: discord.guild, sheet: str, region: str, index:int, vals: list, rangeFix: tuple = (0, 0)):
    '''Replaces data at a specific index location'''
    if not self.bot.edit_mode: return True
    config = GetGuildConfig(guild)

    region = config["source"]["regions"][region].split(":")
    _, row = splitCell(region[1])

    if config["source"]["type"] == "sheets":
      region[0] = mathCell(region[0], rangeFix[0], index)
      region[1] = mathCell(region[0], rangeFix[1] + row, index)

      output = Sheets_API.Write(config, sheet, ":".join(region), vals)
      return output.get('updatedCells') != 0

    return False

  def replaceOnWaitlist(self, guild: discord.guild, receipt: dict, index: int):
    return self.ReplaceToSource(guild, "Waitlist", "waitlist", index,
    [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]],
    # ! WARNING: Brute force fix for data
    rangeFix=(1, 0)
  )

  def deleteOnWaitlist(self, guild: discord.Guild, index: int):
    '''Shortcut for receipt = blank'''
    return self.replaceOnWaitlist(guild, GenerateBlankReceipt(), index)

  def findWaitlistReceipt(self, guild: discord.Guild, user: discord.Member):
    if not self.bot.edit_mode: return True
    config = GetGuildConfig(guild)

    if config["source"]["type"] == "sheets":
      receipts = []

      range = config["source"]["regions"]["waitlist"]
      data = Sheets_API.Query(config, "Waitlist", range)

      for _, row in enumerate(data):
        if len(row) <= 1: continue
        if row[1] == user.name + "#" + str(user.discriminator):
          receipt = {
            "row": int(row[0]),
            "disc_id": row[1],
            "union": row[4],
            "n_ign": row[2],
            "n_id": row[3],
            "notes": row[5],
            "date": int(row[6])
          }
          receipts.append(receipt)
      return None if len(receipts) == 0 else receipts
    
    return None

  # --------------------------------------
  # ! + App Commands
  # --------------------------------------
  @app_commands.command(name="union_join", description="Join a Union!")
  async def union_join(self, interaction: discord.Interaction, options: str = "", member: discord.Member = None):    
    if options == "":
      # ? Message: INFORM OPTIONS
      await interaction.response.send_message(f"Hey {interaction.user.mention}! Click on one of our unions to add yourself to the waitlist.", view=SelectUnion(self), ephemeral=True)
    elif options == "edit":
      await interaction.response.send_message("This is not implemented yet! Please try another command", ephemeral=True)
    elif options == "cancel":
      receipts = self.findWaitlistReceipt(interaction.guild, interaction.user)
      if not receipts: 
        await interaction.response.send_message("We couldn't find you on the waitlist! That means you haven't applied yet", ephemeral=True)
        return

      embed = Union.generateReceiptEmbed(receipts[0])
      embed.set_field_at(0, name="Discord ID", value=interaction.user.mention)

      await interaction.response.send_message("Please confirm whether you would like to remove this entry.", embed = embed, view=RemoveWaitlist(self, receipts[0]), ephemeral=True)
      return

    elif options == "help":
      await interaction.response.send_message("**Temporary help message**\n`/union-join` - Put an entry for yourself on waitlist for a union\n`/union-join options:edit` - Edit an entry for yourself on waitlist\n`/union-join options:cancel` - Remove an entry for yourself on waitlist for a union\n`/union-join options:help` - Shows this message")
      return

    elif options == "accept":
      if not interaction.permissions.manage_guild:
        await interaction.response.send_message("You do not have permission to use this command option.", ephemeral=True)
        return

      # Find if they do have a receipt
      receipts = self.findWaitlistReceipt(interaction.guild, member)
      if len(receipts) == 0:
        await interaction.response.send_message("This user does not have any entries for a union.")
        return

      if not self.addToRoster(interaction.guild, receipts[0]):
        await interaction.response.send_message("There was an error adding this person to the roster.")
        return
      
      await interaction.channel.send(f"{interaction.user.mention} has accepted {member.mention} to {receipts[0]['union']}.")

      try:
        await member.send(f"Congratulations! You\'ve been accepted into Nikke - {receipts[0]['union']}")
      except:
        # Get the system channel
        config = GetGuildConfig(interaction.guild)
        await interaction.guild.get_channel(config["channels"]["bot-status"]).send(f"Congratulations! You\'ve been accepted into Nikke - {receipts[0]['union']}")

      if not self.deleteOnWaitlist(interaction.guild, receipts[0]["row"]):
        await interaction.response.send_message("There was an error removing this person from the waitlist, please remove them manually")
      return

    elif options == "deny":
      if not interaction.permissions.manage_guild:
        await interaction.response.send_message("You do not have permission to use this command option.", ephemeral=True)
        return
      
      # Find if they do have a receipt
      receipts = self.findWaitlistReceipt(interaction.guild, member)
      if len(receipts) == 0:
        await interaction.response.send_message("This user does not have any entries for a union.")
        return

      if not self.deleteOnWaitlist(interaction.guild, receipts[0]["row"]):
        await interaction.response.send_message("There was an error removing this person from the waitlist, please remove them manually")
        return

      try:
        await member.send(f"Sorry! You\'ve been rejected for joining Nikke - {receipts[0]['union']}")
      except:
        # Get the system channel
        config = GetGuildConfig(interaction.guild)
        await interaction.guild.get_channel(config["channels"]["bot-status"]).send(f"Sorry! You\'ve been rejected for joining Nikke - {receipts[0]['union']}")

      return


  @staticmethod
  def generateReceiptEmbed(receipt):
    embed: discord.Embed = discord.Embed(
        colour = discord.Color.blue(),
        title = "POLI-CE FORCE Union Waitlist Receipt",
        type= 'rich'
    )

    embed.add_field(name="Discord ID", value=receipt["disc_id"])
    embed.add_field(name="Target Union", value=receipt["union"])
    embed.add_field(name="Nikke IGN", value=receipt["n_ign"])
    embed.add_field(name="Nikke ID", value=receipt["n_id"])
    embed.add_field(name="Additional Notes", value=receipt["notes"], inline=False)
    embed.add_field(name="Date submitted", value=f'<t:{receipt["date"]}:F>')

    return embed

# --------------------------------------
# ! + Displays
# --------------------------------------

class SelectUnion(ui.View):
  def __init__(self, parent: Union):
    super().__init__()
    self.parent = parent
  @ui.button(label="Police", style=discord.ButtonStyle.blurple)
  async def joinPolice(self, interaction: discord.Interaction, button: discord.Button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Police"))
  @ui.button(label="Polidogs", style=discord.ButtonStyle.green)
  async def joinPolidogs(self, interaction: discord.Interaction, button: discord.Button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Polidogs"))
  @ui.button(label="Polipups", style=discord.ButtonStyle.red)
  async def joinPoliups(self, interaction: discord.Interaction, button: discord.Button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Polipups"))

class RemoveWaitlist(ui.View):
  def __init__(self, parent, receipt):
    super().__init__()
    self.parent = parent
    self.receipt = receipt
  @ui.button(label="Leave", style=discord.ButtonStyle.red)
  async def leave(self, interaction: discord.Interaction, button):
    self.receipt = {
      "row": self.receipt["row"],
      "disc_id": "",
      "union": "",
      "n_ign": "",
      "n_id": "",
      "notes": "",
      "date": ""
    }

    if (not self.parent.replaceOnWaitlist(interaction.guild, self.receipt, self.receipt["row"])):
      await interaction.response.send_message("An error occured.", ephemeral=True)
      return

    try:
      await interaction.user.send("Your application has been removed from our waitlist.")
    except discord.errors.DiscordException:
      await interaction.response.send_message("Your application has been removed from our waitlist.", ephemeral=True)
    pass

  @ui.button(label="Cancel", style=discord.ButtonStyle.gray)
  async def cancel(self, interaction: discord.Interaction):
    await interaction.delete_original_response()

class JoinForm(ui.Modal):
  def __init__(self, parent: Union, title):
    super().__init__(title=title)
    self.parent = parent

  nid = ui.TextInput(label="Player ID", style= discord.TextStyle.short, max_length=8,  min_length=8)
  name = ui.TextInput(label="Name", style= discord.TextStyle.short, max_length=20)
  notes = ui.TextInput(label="Additional Notes", style=discord.TextStyle.paragraph,  max_length=400, required=False)
  
  async def on_submit(self, interaction: discord.Interaction):
    t = datetime.now()
    receipt = {
      "disc_id": interaction.user.name + "#" + str(interaction.user.discriminator),
      "union": self.title.split(" ")[2],
      "n_ign": self.name.value,
      "n_id": self.nid.value,
      "notes": self.notes.value,
      "date": int(t.timestamp())
    }

    if not self.parent.addReceiptToWaitlist(interaction.guild, receipt):
      await interaction.response.send_message("An error occured.", ephemeral=True)
      return
    
    embed = Union.generateReceiptEmbed(receipt)
    embed.set_field_at(0, name="Discord ID", value=interaction.user.mention)

    try:
      await interaction.response.defer()
      await interaction.user.send("All set! Please wait for a response as union leaders do their thing.", embed=embed)
    except discord.errors.DiscordException:
      await interaction.response.send_message("Since I can't send a DM, I'll send the receipt here. Screenshot this to keep a record of it.", embed=embed, ephemeral=True)
    await interaction.delete_original_response()