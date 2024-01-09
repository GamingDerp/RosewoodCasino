import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

class CrashGame:
    def __init__(self):
        self.game_running = False
        self.game_multiplier = 0.0
        self.players = []

class CrashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crash_game = CrashGame()

    async def deduct_balance(self, user_id, amount):
        async with aiosqlite.connect('dbs/balance.db') as db:
            async with db.execute('SELECT account_balance FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                user_balance = await cursor.fetchone()
            if user_balance and user_balance[0] >= amount:
                new_balance = user_balance[0] - amount
                await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                await db.commit()
                return True
        return False

    async def add_balance(self, user_id, amount):
        async with aiosqlite.connect('dbs/balance.db') as db:
            async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                user_account = await cursor.fetchone()
            if user_account:
                new_balance = user_account[1] + amount
                await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                await db.commit()
                return True
        return False

    @commands.hybrid_command(description="Join the current game of Crash")
    async def buy(self, ctx, bet: float):
        if ctx.prefix == "!" and ctx.invoked_with in ["buy"]:
            return
        crchannel = 1166171307923214426
        bdchannel = 1163616023073783938
        user_id = ctx.author.id
        async with aiosqlite.connect('dbs/balance.db') as db:
            async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                user_account = await cursor.fetchone()
            if not user_account:
                e.title = "❓ Account Not Found ❓"
                e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                await ctx.send(embed=e, ephemeral=True)
                return
        if ctx.channel.id == crchannel or ctx.channel.id == bdchannel:
            try:
                min_bet = 25
                max_bet = 25000
                e = discord.Embed(color=0xff5f39)
                formatted_bet = "${:,.2f}".format(bet)
                if self.crash_game.game_running:
                    if bet < min_bet:
                        e.title = "💰 Minimum Bet 💰"
                        e.description = "The minimum bet for **Crash** is **$25**!"
                        await ctx.send(embed=e, ephemeral=True)
                    elif bet > max_bet:
                        e.title = "💰 Maximum Bet 💰"
                        e.description = "The maximum bet for **Crash** is **$25,000**!"
                        await ctx.send(embed=e, ephemeral=True)
                    elif await self.deduct_balance(ctx.author.id, bet):
                        self.crash_game.players.append((ctx.author, bet))
                        e.title = "✅ You Joined ✅"
                        e.description = f"💎 {formatted_bet}"
                        e.set_footer(text=f"Good luck!")
                        await ctx.send(embed=e, ephemeral=True)
                    else:
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"You are unable to bet **{formatted_bet}**!"
                        await ctx.send(embed=e, ephemeral=True)
                else:
                    e.title = "❌ Unable To Join ❌"
                    e.description = "No game is currently running! Do `/crash` to start one!"
                    await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                traceback.print_exc()
                print(e)
            except discord.errors.NotFound as e:
                traceback.print_exc()
                print(e)
            except discord.errors.HTTPException as e:
                traceback.print_exc()
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1166171307923214426> to use **Buy**!"
            await ctx.send(embed=e, ephemeral=True)
            return

    @commands.hybrid_command(description="Exit the current game of Crash")
    async def out(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["out"]:
            return
        crchannel = 1166171307923214426
        bdchannel = 1163616023073783938
        user_id = ctx.author.id
        async with aiosqlite.connect('dbs/balance.db') as db:
            async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                user_account = await cursor.fetchone()
            if not user_account:
                e.title = "❓ Account Not Found ❓"
                e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                await ctx.send(embed=e, ephemeral=True)
                return
        if ctx.channel.id == crchannel or ctx.channel.id == bdchannel:
            try:
                e = discord.Embed(color=0xff5f39)
                if self.crash_game.game_running:
                    player_removed = False
                    for i, (player, bet) in enumerate(self.crash_game.players):
                        if player == ctx.author:
                            winnings = bet * self.crash_game.game_multiplier
                            formatted_winnings = "${:,.2f}".format(winnings)
                            await self.add_balance(ctx.author.id, winnings)
                            self.crash_game.players.pop(i)
                            e.title = "❌ You're Out! ❌"
                            e.description = "You left the game!" 
                            e.add_field(
                                name="Multiplier",
                                value=f"📈 {self.crash_game.game_multiplier:.2f}x",
                                inline=False
                            )
                            e.add_field(
                                name="Winnings",
                                value=f"💎 {formatted_winnings}",
                                inline=False
                            )
                            e.set_footer(text=f"Congrats!")
                            await ctx.send(embed=e, ephemeral=True)
                            break
                    else:
                        e.title = "❌ Unable To Join ❌"
                        e.description = "You are not part of the current game. Wait till the next game starts!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                else:
                    e.title = "❌ Unable To Join ❌"
                    e.description = "No game is currently running! Do `/crash` to start one!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
            except Exception as e:
                traceback.print_exc()
                print(e)
            except discord.errors.NotFound as e:
                traceback.print_exc()
                print(e)
            except discord.errors.HTTPException as e:
                traceback.print_exc()
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1166171307923214426> to use **Out**!"
            await ctx.send(embed=e, ephemeral=True)
            return
    
    async def crash_game_logic(self, ctx, crash_game):
        try:
            crash_game.game_running = True
            max_multiplier = 5.0
            final_multiplier_ranges = [
                (0.01, 0.95, 0.15),
                (0.95, 1.45, 0.20),
                (1.45, 1.95, 0.25),
                (1.95, 2.45, 0.70),
                (2.45, 2.95, 0.50),
                (2.95, 3.45, 0.30),
                (3.45, 3.95, 0.15),
                (3.95, 4.45, 0.05),
                (4.45, 4.95, 0.03),
                (4.95, 5.0, 0.01),
            ]
            final_multiplier = 0.01
            for start, end, chance in final_multiplier_ranges:
                if random.uniform(0, 1) <= chance:
                    final_multiplier = round(random.uniform(start, end), 2)
                    break
            countdown_embed = discord.Embed(
                title="⏳ Crash Game Starting... ⏳",
                color=0xff5f39,
            )
            e = discord.Embed(
                title="⏳ Crash Game Starting... ⏳",
                color=0xff5f39,
            )
            e.set_footer(text="Do /buy <bet> to join the game!")
            message = await ctx.send(embed=e)
            for remaining_time in range(30, 0, -1):
                countdown_embed.clear_fields()
                countdown_embed.add_field(
                    name="Starting In",
                    value=f"⏰ **{remaining_time}** seconds...",
                )
                countdown_embed.set_footer(text="Do /buy <bet> to join the game!")
                await message.edit(embed=countdown_embed)
                await asyncio.sleep(1)
            crash_game.game_multiplier = 0.01
            while crash_game.game_multiplier < final_multiplier:
                await asyncio.sleep(1)
                if not crash_game.game_running:
                    break
                crash_game.game_multiplier = round(crash_game.game_multiplier + random.uniform(0.01, 0.06), 2)
                countdown_embed.title = "🚀 Crash 🚀"
                countdown_embed.clear_fields()
                countdown_embed.add_field(
                    name="Multiplier",
                    value=f"📈 {crash_game.game_multiplier:.2f}x",
                )
                countdown_embed.set_footer(text="Do /out to bail!")
                await message.edit(embed=countdown_embed)
            e.title = "💥 It Crashed! 💥"
            e.clear_fields()
            e.add_field(
                name="Final Multiplier",
                value=f"📈 {crash_game.game_multiplier:.2f}x",
            )
            e.set_footer(text="Crashed! Do /crash to start a new game!")
            await message.edit(embed=e)
            crash_game.players.clear()
            for player in crash_game.players[:]:
                if not any(player[0] == user for user, _ in crash_game.players_out):
                    crash_game.players.remove(player)
        except Exception as e:
            print(e)

    @commands.hybrid_command(description="Start a game of Crash")
    async def crash(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["crash"]:
            return
        crchannel = 1166171307923214426
        bdchannel = 1163616023073783938
        user_id = ctx.author.id
        async with aiosqlite.connect('dbs/balance.db') as db:
            async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                user_account = await cursor.fetchone()
            if not user_account:
                e.title = "❓ Account Not Found ❓"
                e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                await ctx.send(embed=e, ephemeral=True)
                return
        if ctx.channel.id == crchannel or ctx.channel.id == bdchannel:
            try:
                self.crash_game = CrashGame()
                self.crash_game.game_running = True
                await self.crash_game_logic(ctx, self.crash_game)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1166171307923214426> to use **Crash**!"
            await ctx.send(embed=e, ephemeral=True)
            return 


async def setup(bot):
    await bot.add_cog(CrashCog(bot))