import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

class SixesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Play a game of sixes! Costs $100!")
    async def sixes(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["sixes"]:
            return
        sxchannel = 1173077222932881480
        bdchannel = 1163616023073783938
        if ctx.channel.id == sxchannel or ctx.channel.id == bdchannel:
            try:
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                        user_account = await cursor.fetchone()
                    e = discord.Embed(color=0xff5f39)
                    if user_account:
                        balance = user_account[1]
                        if balance < 100:
                            e.title = "⛔️ Insufficient Balance ⛔️"
                            e.description = f"You are unable to bet **$100**!"
                            await ctx.send(embed=e, ephemeral=True)
                            return
                        balance -= 100
                        await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (balance, user_id))
                        await db.commit()
                    else:
                        e.title = "❓ Account Not Found ❓"
                        e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                results = []
                for _ in range(6):
                    random_number = random.randint(1, 100)
                    if random_number <= 80:
                        results.append(random.randint(1, 5))
                    else:
                        results.append(6)
                result_description = " ".join(map(str, results))
                if all(num == 6 for num in results):
                    async with aiosqlite.connect('dbs/balance.db') as db:
                        await db.execute('UPDATE accounts SET account_balance = account_balance + ? WHERE user_id = ?', (100000, user_id))
                        await db.commit()
                    e = discord.Embed(title="🏆 You Win! 🏆", color=0xFdc400, description=result_description)
                    await ctx.send(f"Congratulations {ctx.author.mention}! You won **$100,000**! :tada:", embed=e)
                else:
                    e = discord.Embed(title="🧮 Sixes 🧮", color=0xff5f39, description=result_description)
                    await ctx.send(embed=e)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1173077222932881480> to use **Sixes**!"
            await ctx.send(embed=e, ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(SixesCog(bot))    