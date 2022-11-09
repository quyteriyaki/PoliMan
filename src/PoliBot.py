from discord.ext import commands
from src.workspace import Workspace
import discord

from src.components.Registration import Registration
from src.components.Administration import Administration

class PoliBot(commands.bot.Bot):
  def __init__(self, *, command_prefix: str, intents: discord.Intents, workspace: Workspace):
    super().__init__(command_prefix=command_prefix, intents=intents)
    self.work = workspace
    self.paths = {}
    self.configs: dict = {}
    self.spreadsheet_mode = False

  async def setup(self):
    await self.add_cog(Registration(self))

  def PassConfigs(self, paths, configs):
    self.paths = paths
    self.configs = configs

  async def on_ready(self):
    await self.setup()
    guild = discord.Object(id=105518865928212480)
    self.tree.copy_global_to(guild = guild)
    await self.tree.sync(guild = guild)
    print(f'{self.user} is ready!')