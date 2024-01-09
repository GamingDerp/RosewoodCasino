import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Play a game of Roulette")
    async def roulette(self, ctx, bet: int, color: str=None, number: int=None, odds: str=None):
        if ctx.prefix == "!" and ctx.invoked_with in ["roulette"]:
            return
        rlchannel = 1171955332537385041
        bdchannel = 1163616023073783938
        min_bet = 25
        max_bet = 25000
        if ctx.channel.id == rlchannel or ctx.channel.id == bdchannel:
            try:
                if bet is None:
                    return
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                    user_account = await cursor.fetchone()
                    e = discord.Embed(color=0xff5f39)
                    if not user_account:
                        e.title = "❓ Account Not Found ❓"
                        e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if bet < min_bet:
                        e.title = "💰 Minimum Bet 💰"
                        e.description = "The minimum bet for **Roulette** is **$25**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if bet > max_bet:
                        e.title = "💰 Maximum Bet 💰"
                        e.description = "The maximum bet for **Roulette** is **$25,000**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    account_balance = user_account[1]
                    if bet > account_balance:
                        formatted_bet = "${:,.2f}".format(bet)
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"You are unable to bet **{formatted_bet}**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    selected_options = [option for option in [color, number, odds] if option]
                    if len(selected_options) > 1:
                        e.title = "⚠️ Invalid Selection ⚠️"
                        e.description = "You can only choose one option at a time (color, number, or odds)!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    results = []
                    win_message = []
                    total_winnings = 0
                    if color == "Black".lower():
                        color_num = random.randint(1, 100)
                        if color_num <= 50:
                            result_color = "Red"
                            results.append(f"❌ **Color:** {result_color}")
                        else:
                            result_color = "Black"
                            total_winnings += bet * 2
                            results.append(f"✅ **Color:** {result_color}")
                    elif color == "Red".lower():
                        color_num = random.randint(1, 100)
                        if color_num <= 50:
                            result_color = "Black"
                            results.append(f"❌ **Color:** {result_color}")
                        else:
                            result_color = "Red"
                            total_winnings += bet * 2
                            results.append(f"✅ **Color:** {result_color}")
                    if number:
                        chosen_number = random.randint(1, 36)
                        is_number_correct = number == chosen_number
                        results.append(f"{'✅' if number == chosen_number else '❌'} **Number:** {chosen_number}")
                        if is_number_correct:
                            total_winnings += bet * 5
                    if odds == "Even".lower():
                        odds_num = random.randint(1, 100)
                        if odds_num <= 50:
                            result_num = "Odd"
                            results.append(f"❌ **Odds:** {result_num}")
                        else:
                            result_num = "Even"
                            total_winnings += bet * 2
                            results.append(f"✅ **Odds:** {result_num}")
                    elif odds == "Odd".lower():
                        odds_num = random.randint(1, 100)
                        if odds_num <= 50:
                            result_num = "Even"
                            results.append(f"❌ **Odds:** {result_num}")
                        else:
                            result_num = "Odd"
                            total_winnings += bet * 2
                            results.append(f"✅ **Odds:** {result_num}")
                    if not results:
                        return
                    new_balance = user_account[1] + total_winnings - bet
                    formatted_winnings = "${:,.2f}".format(total_winnings)
                    await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                    await db.commit()
                    e = discord.Embed(title="🎲 Roulette 🎲", color=0xff5f39)
                    e.add_field(name="📋 Result", value="\n".join(results), inline=False)
                    if total_winnings > 0:
                        e.add_field(name="💰 Winnings", value=f"{formatted_winnings}", inline=False)
                        e.description = "You win! :tada:"
                    await ctx.send(embed=e)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1171955332537385041> to use **Roulette**!"
            await ctx.send(embed=e, ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(RouletteCog(bot))