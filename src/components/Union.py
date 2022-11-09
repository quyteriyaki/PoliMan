from discord.ext import commands
from discord import app_commands
import discord
import discord.ui as ui
from src.workspace_utils import *

from datetime import datetime

class Union(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # --------------------------------------
  # + Bot
  # --------------------------------------
  def addReceiptToWaitlist(self, receipt) -> bool:
    if not self.bot.spreadsheet_mode: return True

    vals = [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]]
    range = self.bot.configs["workspace"]["regions"]["waitlist"]
  
    data = self.bot.work.Query("Waitlist", range)
    rowRange = FindEmptyRow(data, range, excludeCount = 1)

    # Nudge across 1 so we don't mess up the numbers on the side
    rowRange[0] = mathCell(rowRange[0], 1, 0)

    output = self.bot.work.Write("Waitlist", ":".join(rowRange), vals)
    return output.get('updatedCells') != 0

  def replaceOnWaitList(self, receipt, index):
    '''Explicitly replaces content at a location'''
    if not self.bot.spreadsheet_mode: return True

    vals = [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]]

    range = self.bot.configs["workspace"]["regions"]["waitlist"].split(":")
    # Change the index to start + row
    range[0] = mathCell(range[0], 1, index)
    range[1] = mathCell(range[0], 6, index)

    output = self.bot.work.Write("Waitlist", ":".join(range), vals)
    return output.get('updatedCells') != 0

  def findReceipt(self, user: discord.Member):
    if not self.bot.spreadsheet_mode: return True

    data = self.bot.work.Query("Waitlist",
      self.bot.configs["workspace"]["regions"]["waitlist"])

    receipts = []

    for i, row in enumerate(data):
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
    if len(receipts) == 0: return None
    return receipts


  @app_commands.command(name="union_join", description="Start the process to join a Union!")
  async def union_join(self, interaction: discord.Interaction, options: str = "", member: discord.Member = None):    
    if options == "":
      # Default action is for that user to engage in the process
      await interaction.response.send_message(f"Hey {interaction.user.mention}! Click on one of our unions to add yourself to the waitlist.", view=SelectUnion(self))
    elif options == "edit":
      await interaction.response.send_message("This is not implemented yet! Please try another command")
    elif options == "cancel":
      # Show receipts
      # Confirmation message
      receipts = self.findReceipt(interaction.user)
      if not receipts: 
        await interaction.response.send_message("We couldn't find you on the waitlist! That means you haven't applied yet")
        return

      embed = Union.generateReceiptEmbed(receipts[0])
      embed.set_field_at(0, name="Discord ID", value=interaction.user.mention)

      await interaction.response.send_message("Please confirm whether you would like to remove this entry.", embed = embed, view=RemoveWaitlist(self, receipts[0]))

    elif options == "accept":
      pass

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

    if (not self.parent.replaceOnWaitList(self.receipt)) :
      await interaction.response.send_message("An error occured.")
      return

    try:
      await interaction.user.send("Your application has been removed from our waitlist.")
    except discord.errors.DiscordException:
      await interaction.response.send_message("Your application has been removed from our waitlist.")
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

    if not self.parent.addReceiptToWaitlist(receipt):
      await interaction.response.send_message("An error occured.")
      return
    
    embed = Union.generateReceiptEmbed(receipt)
    embed.set_field_at(0, name="Discord ID", value=interaction.user.mention)

    try:
      await interaction.response.defer()
      await interaction.user.send("All set! Please wait for a response as union leaders do their thing.", embed=embed)
    except discord.errors.DiscordException:
      await interaction.response.send_message("Since I can't send a DM, I'll send the receipt here. Screenshot this to keep a record of it.", embed=embed)
    await interaction.delete_original_response()