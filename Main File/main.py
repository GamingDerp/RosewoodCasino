import os
import discord
import asyncio
import aiosqlite
from discord.utils import get
from discord.ext import commands
from datetime import datetime, timedelta
import time

# Bot Intents & Defining Bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command('help')    

# Loading Cogs
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            
async def main():
    await load()
    await bot.start("TOKEN")
    
# Startup Event
@bot.listen()
async def on_ready():
    await print(f"Logged in as {bot.user} \nID: {bot.user.id}")

@bot.command()
async def reload(ctx, cog_name: str):
    if discord.utils.get(ctx.author.roles, name="Casino Owner"):
        try:
            await bot.unload_extension(f"cogs.{cog_name}")
            await bot.load_extension(f"cogs.{cog_name}")
            await ctx.send(f"**{cog_name}** has been reloaded successfully!")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"{cog_name} is not loaded.")
        except commands.ExtensionNotFound:
            await ctx.send(f"{cog_name} does not exist.")
        except Exception as e:
            await ctx.send(f"An error occurred while reloading {cog_name}: {e}")
    else:
        e = discord.Embed(color=0xff5f39)
        e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
        await ctx.send(embed=e)

@bot.command()
async def loadcog(ctx, cog_name: str):
    if discord.utils.get(ctx.author.roles, name="Casino Owner"):
        try:
            await bot.load_extension(f"cogs.{cog_name}")
            await ctx.send(f"**{cog_name}** has been loaded successfully!")
        except commands.ExtensionNotFound:
            await ctx.send(f"{cog_name} does not exist.")
        except Exception as e:
            await ctx.send(f"An error occurred while loading {cog_name}: {e}")
    else:
        e = discord.Embed(color=0xff5f39)
        e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
        await ctx.send(embed=e)

@bot.command()
async def unloadcog(ctx, cog_name: str):
    if discord.utils.get(ctx.author.roles, name="Casino Owner"):
        try:
            await bot.unload_extension(f"cogs.{cog_name}")
            await ctx.send(f"**{cog_name}** has been unloaded successfully!")
        except commands.ExtensionNotFound:
            await ctx.send(f"{cog_name} does not exist.")
        except Exception as e:
            await ctx.send(f"An error occurred while unloading {cog_name}: {e}")
    else:
        e = discord.Embed(color=0xff5f39)
        e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
        await ctx.send(embed=e)

@bot.command()
async def sync(ctx):
    if discord.utils.get(ctx.author.roles, name="Casino Owner"):
        try:
            await bot.tree.sync()
            await ctx.send("The bot has been synced!")
        except Exception as e:
            await ctx.send(f"An error occurred while syncing: {e}")
    else:
        e = discord.Embed(color=0xff5f39)
        e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
        await ctx.send(embed=e)

asyncio.run(main())