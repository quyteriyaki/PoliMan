import discord
import discord.ui as ui

from datetime import datetime, time

def GenerateReceipt(discord_ID: str, union: str, nikke_IGN: str, nikke_ID: str, notes:str, date: int = None):
  return {
    "disc_id": discord_ID,
    "union": union, 
    "n_ign": nikke_IGN,
    "n_id": nikke_ID,
    "notes": notes,
    "date": date
  }

def GenerateBlankReceipt():
  return GenerateReceipt("", "", "", "", "", None)