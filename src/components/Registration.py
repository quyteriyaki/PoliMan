from discord.ext import commands
from discord import app_commands
import discord
import discord.ui as ui
from src.workspace_utils import *

from datetime import datetime

class Registration(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="join", description="Start the process to join a Union!")
  async def join(self, interaction: discord.Interaction):
    await interaction.response.send_message("Click on one of our unions to add yourself to the waitlist.", view=SelectUnion(self))

  def addReceiptToWaitlist(self, receipt):
    vals = [[receipt["disc_id"], receipt["n_ign"], receipt["n_id"], receipt["union"], receipt["notes"], receipt["date"]]]
    
    range = self.bot.configs["workspace"]["regions"]["waitlist"]
    data = self.bot.work.Query("Waitlist", range)
    rowRange = FindEmptyRow(data, range.split(":")[0])
    rowRange[0] = mathCell(rowRange[0], 1, 0)

    output = self.bot.work.Write("Waitlist", ":".join(rowRange), vals)
    return output.get('updatedCells') != 0

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
      embed: discord.Embed = discord.Embed(
        colour = discord.Color.blue(),
        title = "POLI-CE FORCE Union Waitlist Receipt",
        type= 'rich'
      )

      embed.add_field(name="Discord ID", value=interaction.user.mention)
      embed.add_field(name="Target Union", value=receipt["union"])
      embed.add_field(name="Nikke IGN", value=receipt["n_ign"])
      embed.add_field(name="Nikke ID", value=receipt["n_id"])
      embed.add_field(name="Additional Notes", value=receipt["notes"], inline=False)
      embed.add_field(name="Date submitted", value=f'<t:{int(t.timestamp())}:F>')

      try:
        await interaction.user.send(embed=embed)
      except Exception:
        await interaction.response.send_message("Since I can't send a DM, I'll send the receipt here.", embed=embed)
    else:
      await interaction.response.send_message("An error occured.")