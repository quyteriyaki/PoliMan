from discord.ext import commands
import discord
import json
import os

from src.components.Union import Union
from src.components.Administration import Administration

class PoliBot(commands.bot.Bot):
  def __init__(self, *, command_prefix: str, intents: discord.Intents):
    super().__init__(command_prefix=command_prefix, intents=intents)
    self.paths = {}
    self.configs: dict = {}
    self.edit_mode = True
    self.build_mode = "development"

  async def Setup(self):
    await self.add_cog(Union(self))
    await self.add_cog(Administration(self))
    return

  async def PerGuildInitialization(self):
    guilds: list(str) = []
    if self.build_mode == "development":
      with open("config/config.json", "r") as file:
        guilds = json.load(file)["dev_servers"]
    elif self.build_mode == "production":
      guilds = os.listdir('config/servers')

    for i in self.guilds:
      # Sync to guilds
      self.tree.copy_global_to(guild=i)

      # Notify Launch
      channel: discord.guild.GuildChannel = i.system_channel
      if i.id not in guilds:
        # TODO: Notify guild that setup is required before use
        # ? MESSAGE: ONLINE + ERROR - CONFIG_NOT_SET
        await channel.send("Poli is online!\n" + f"ERROR: No config file found. Please do `/setup` before using the bot.")
      else:
        with open(f"config/servers/{i.id}/config.json", 'r') as file:
          config = json.load(file)
          try:
            channel_id=config["channels"]["bot-status"]
            channel = i.get_channel(channel_id)
            # ? MESSAGE: ONLINE + INFO - STATUS OKAY
            await channel.send("Poli is online!\nEverything is set here, you're ready to use the bot!")
          except KeyError:
            # ? MESSAGE: ONLINE + WARNING - STATUS_CHANNEL_NOT_SET
            await channel.send("Poli is online!\n" + f"WARNING: No bot specific channel. All server messages will go to {channel.mention}.")

  @commands.Cog.listener()
  async def on_guild_join(self, guild: discord.Guild):
    # TODO: Welcome Message
    guilds = os.listdir('config/servers')
    
    if guild.id not in guilds:
      # TODO: Notify guild that setup is required before use
      pass
    else:
      # ! They have used this bot before. Depict some sample configuration details & ask whether to keep or to remove
      pass

  async def on_ready(self):
    await self.Setup()
    await self.tree.sync()
    print(f'{self.user} is ready!')
    await self.PerGuildInitialization()