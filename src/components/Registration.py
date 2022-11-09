from discord.ext import commands
from discord import app_commands
import discord
import discord.ui as ui
from src.workspace_utils import *

from datetime import datetime, date

class Registration(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

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
      await interaction.response.send_message("This is not implemented yet! Please try another command")
    elif options == "accept":
      pass

  def getWaitlistData(self):
    range = self.bot.configs["workspace"]["regions"]["waitlist"]
    return self.bot.work.Query("Waitlist", range)

  def addReceiptToWaitlist(self, receipt):
    if not self.bot.spreadsheet_mode: return True
    vals = [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]]
    
    data = self.getWaitlistData()
    rowRange = FindEmptyRow(data, range.split(":")[0])
    rowRange[0] = mathCell(rowRange[0], 1, 0)

    output = self.bot.work.Write("Waitlist", ":".join(rowRange), vals)
    return output.get('updatedCells') != 0

  def findReceipt(self, user: discord.Member):
    if not self.bot.spreadsheet_mode: return True
    data = self.getWaitlistData()

    receipts = []

    for row in data:
      if row[0] == user.name + "#" + str(user.discriminator):
        receipt = {
          "disc_id": row[0],
          "union": row[3],
          "n_ign": row[1],
          "n_id": row[2],
          "notes": row[4],
          "date": row[5]
        }

        r = receipt["date"].split("/")
        receipt["date"] = date(r[2], r[0]. r[1])

        receipts.append(receipt)
    return receipts

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
    embed.add_field(name="Date submitted", value=receipt["date"])
    return embed

class SelectUnion(ui.View):
  def __init__(self, parent):
    super().__init__()
    self.parent = parent
  @ui.button(label="Police", style=discord.ButtonStyle.blurple)
  async def joinPolice(self, interaction: discord.Interaction, button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Police"))
  @ui.button(label="Polidogs", style=discord.ButtonStyle.green)
  async def joinPolidogs(self, interaction: discord.Interaction, button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Polidogs"))
  @ui.button(label="Polipups", style=discord.ButtonStyle.red)
  async def joinPoliups(self, interaction: discord.Interaction, button):
    await interaction.response.send_modal(JoinForm(parent=self.parent, title="Signup for Polipups"))
  
class JoinForm(ui.Modal):
  def __init__(self, parent: Registration, title):
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
      "date": t.strftime("%m/%d/%Y")
    }

    if (self.parent.addReceiptToWaitlist(receipt)):
      embed = Registration.generateReceiptEmbed(receipt)

      embed.set_field_at(0, name="Discord ID", value=interaction.user.mention)
      embed.set_field_at(5, name="Date submitted", value=f'<t:{int(t.timestamp())}:F>')

      try:
        await interaction.response.defer()
        await interaction.user.send("All set! Please wait for a response as union leaders do their thing.", embed=embed)
      except discord.errors.DiscordException:
        await interaction.response.send_message("Since I can't send a DM, I'll send the receipt here.", embed=embed)
      await interaction.delete_original_response()
    else:
      await interaction.response.send_message("An error occured.")