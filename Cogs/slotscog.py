import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

class SlotsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.result = []

    @commands.hybrid_command(description="Play a game of slots")
    async def slots(self, ctx, bet: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["slots"]:
            return
        slchannel = 1163621079286288384
        bdchannel = 1163616023073783938
        min_bet = 25
        max_bet = 25000
        if ctx.channel.id == slchannel or ctx.channel.id == bdchannel:
            try:
                e = discord.Embed(color=0xff5f39)
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                        user_account = await cursor.fetchone()
                    if not user_account:
                        e.title = "❓ Account Not Found ❓"
                        e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    account_balance = user_account[1]
                    if bet < min_bet:
                        e.title = "💰 Minimum Bet 💰"
                        e.description = "The minimum bet for **Slots** is **$25**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if bet > max_bet:
                        e.title = "💰 Maximum Bet 💰"
                        e.description = "The maximum bet for **Slots** is **$25,000**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if bet > account_balance:
                        formatted_bet = "${:,.2f}".format(bet)
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"You are unable to bet **{formatted_bet}**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    new_balance = account_balance - bet
                    await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                    await db.commit()
                symbols = [":cherries:", ":lemon:", ":grapes:", ":bell:", ":game_die:", "<:Cake:1166610828527677450>", "<:Derp:1166610392580116530>"]
                random_values = [random.choice(symbols) for _ in range(3)]
                self.result = random_values
                formatted_result = f"**{' | '.join(random_values)}**"
                def calculate_slots_winnings(result, bet):
                    unique_symbols = set(result)
                    if len(unique_symbols) == 1:
                        return bet * 3
                    elif len(unique_symbols) == 2:
                        return bet * 2
                    else:
                        return 0
                try:
                    winnings = calculate_slots_winnings(random_values, bet)
                    formatted_winnings = "${:,.2f}".format(winnings)
                    if winnings > 0:
                        async with aiosqlite.connect('dbs/balance.db') as db:
                            new_balance += winnings
                            await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                            await db.commit()
                        e.title = ":chart_with_upwards_trend: Winner! :chart_with_upwards_trend:"
                        e.description = f"You won **{formatted_winnings}**"
                        e.add_field(name="Slot Machine", value=formatted_result)
                        await ctx.send(f"{ctx.author.mention} won! :tada:", embed=e)
                        unique_symbols = set(self.result)
                        if len(unique_symbols) == 1:
                            jchannel = self.bot.get_channel(1169163934524264508)
                            e.color = 0xFdc400
                            e.set_image(url="https://media.discordapp.net/attachments/1163615932489416804/1166638067294154822/Jackpot.gif?ex=654b375e&is=6538c25e&hm=fe4fc45fe7110d1c00336b548a304c4ddc59d4051190fa05a55ebb03d665bffe&=")
                            await jchannel.send(f"{ctx.author.mention} got a jackpot! 🏆", embed=e)
                    else:
                        async with aiosqlite.connect('dbs/balance.db') as db:
                            await db.commit()
                        loss_messages = ["Almost There!", "Try Again!", "Nearly Won!", "So Close!"]
                        loss_title = random.choice(loss_messages)
                        e.title = f":chart_with_downwards_trend: {loss_title} :chart_with_downwards_trend:"
                        e.add_field(name="Slot Machine", value=formatted_result)
                        await ctx.send(embed=e)
                except Exception as e:
                    print(e)
            except Exception as e:
                    print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1163621079286288384> to use **Slots**!"
            await ctx.send(embed=e, ephemeral=True)
            return

async def setup(bot):
    await bot.add_cog(SlotsCog(bot))