import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import aiosqlite

class BettingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.createbet_end_time = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.create_table()

    async def create_table(self):
        async with aiosqlite.connect('dbs/betting.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS sides (
                    side_name TEXT PRIMARY KEY,
                    odds REAL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bets (
                    user_id INTEGER,
                    account_number INTEGER,
                    side_name TEXT,
                    bet REAL,
                    PRIMARY KEY (user_id, account_number, side_name)
                )
            ''')
            await db.commit()

    @commands.hybrid_command(description="Start a bet")
    async def createbet(self, ctx, time_limit, side1, side1_odds, side2, side2_odds, side3=None, side3_odds=None, side4=None, side4_odds=None, side5=None, side5_odds=None, side6=None, side6_odds=None, side7=None, side7_odds=None, side8=None, side8_odds=None, side9=None, side9_odds=None, side10=None, side10_odds=None, side11=None, side11_odds=None, side12=None, side12_odds=None):
        if ctx.prefix == "!" and ctx.invoked_with in ["createbet"]:
            return
        cbchannel = 1177498679758827550
        bdchannel = 1163616023073783938
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            if ctx.channel.id == cbchannel or ctx.channel.id == bdchannel:
                try:
                    time_limit_delta = self.convert_duration(time_limit)
                    self.createbet_end_time = datetime.utcnow() + time_limit_delta
                    async with aiosqlite.connect('dbs/betting.db') as db:
                        await db.execute('DELETE FROM sides')
                        await db.execute('DELETE FROM bets')
                        await db.commit()
                        for side, odds_str in [(side1, side1_odds), (side2, side2_odds), (side3, side3_odds), (side4, side4_odds),
                                               (side5, side5_odds), (side6, side6_odds), (side7, side7_odds), (side8, side8_odds),
                                               (side9, side9_odds), (side10, side10_odds), (side11, side11_odds), (side12, side12_odds)]:
                            if side is not None and odds_str is not None:
                                odds = float(odds_str)
                                try:
                                    await db.execute('INSERT INTO sides (side_name, odds) VALUES (?, ?)', (side, odds))
                                except aiosqlite.IntegrityError:
                                    await db.execute('UPDATE sides SET odds = ? WHERE side_name = ?', (odds, side))
                                await db.commit()
                        e = discord.Embed(title="📈 Place your bets! 📈", color=0xff5f39)
                        async with aiosqlite.connect('dbs/betting.db') as db:
                            cursor = await db.execute('SELECT * FROM sides')
                            sides = await cursor.fetchall()
                        for side_info in sides:
                            side_name = side_info[0]
                            odds = side_info[1]
                            e.add_field(name=f"📋 {side_name}", value=f"**Odds:** {odds}x", inline=False)
                    await ctx.send(embed=e)
                    self.bot.loop.create_task(self.check_time_limit(ctx))
                except Exception as e:
                    print(e)
            else:
                e.title = "❌ Incorrect Channel ❌"
                e.description = "This isn't the correct channel! Head to <#1177498679758827550> to use **CreateBet**!"
                await ctx.send(embed=e, ephemeral=True)
                return
        else:
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
            return
    
    async def check_time_limit(self, ctx):
        while datetime.utcnow() < self.createbet_end_time:
            await asyncio.sleep(1)
        await self.send_time_limit_embed(ctx)

    async def send_time_limit_embed(self, ctx):
        e = discord.Embed(title="⏰ Time Ran Out! ⏰", description="Betting time has expired!", color=0xff5f39)
        await ctx.send(embed=e)

    @commands.hybrid_command(description="Make a bet")
    async def bet(self, ctx, side_name, bet):
        if ctx.prefix == "!" and ctx.invoked_with in ["bet"]:
            return
        pbchannel = 1177498697261662208
        bdchannel = 1163616023073783938
        e = discord.Embed(color=0xff5f39)
        if ctx.channel.id == pbchannel or ctx.channel.id == bdchannel:
            try:
                current_time = datetime.utcnow()
                if not self.createbet_end_time or current_time > self.createbet_end_time:
                    e.title = "❌ Unable To Bet ❌"
                    e.description = "Betting time has expired or there is no bet happening!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/betting.db') as db:
                    cursor = await db.execute('''
                        SELECT 1 FROM bets
                        WHERE user_id = ?
                    ''', (user_id,))
                    existing_bets = await cursor.fetchall()
                    if existing_bets:
                        e.title = "🚫 Bet Already Placed 🚫"
                        e.description = "You already placed a bet!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                async with aiosqlite.connect('dbs/betting.db') as db:
                    cursor = await db.execute('SELECT * FROM sides')
                    cursor.row_factory = aiosqlite.Row
                    valid_sides = [side['side_name'] for side in await cursor.fetchall()]
                    if not valid_sides:
                        e.title = "❌ Unable To Bet ❌"
                        e.description = "There's currently no bet happening! Stay tuned for future bets!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if side_name not in valid_sides:
                        e.title = "❌ Invalid Side Input ❌"
                        e.description = f"There is no side called **{side_name}**!"
                        e.add_field(
                            name="Available Sides",
                            value=f"📋 {', '.join(valid_sides)}",
                        )
                        await ctx.send(embed=e, ephemeral=True)
                        return
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                    user_account = await cursor.fetchone()
                if user_account:
                    account_number = user_account[0]
                    current_balance = user_account[1]
                    new_balance = current_balance - float(bet)
                    async with aiosqlite.connect('dbs/balance.db') as db:
                        await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                        await db.commit()
                    formatted_bet = float(bet)
                    if formatted_bet > current_balance:
                        formatted_bet = "${:,.2f}".format(float(bet))
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"You are unable to bet **{formatted_bet}**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if formatted_bet <= 0:
                        e.title = "💰 Minimum Bet 💰"
                        e.description = "The minimum bet is **$1**!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                else:
                    e.title = "❓ Account Not Found ❓"
                    e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                async with aiosqlite.connect('dbs/betting.db') as db:
                    await db.execute('''
                        INSERT INTO bets (user_id, account_number, side_name, bet)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, account_number, side_name, bet))
                    await db.commit()
                formatted_bet = "${:,.2f}".format(float(bet))
                e.title = "✅ Bet Placed ✅"
                e.description = f"📋 {side_name} \n💎 {formatted_bet}"
                e.set_footer(text=f"Good luck!")
                await ctx.send(embed=e, ephemeral=True)
            except ValueError:
                e.title = "❌ Invalid Bet ❌"
                e.description = "Please enter a valid bet amount!"
                await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1177498697261662208> to use **Bet**!"
            await ctx.send(embed=e, ephemeral=True)
            return

    @commands.hybrid_command(description="Choose which side won the bet")
    async def winner(self, ctx, side_name):
        if ctx.prefix == "!" and ctx.invoked_with in ["winner"]:
            return
        cbchannel = 1177498679758827550
        bdchannel = 1163616023073783938
        e = discord.Embed(color=0xff5f39)
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            if ctx.channel.id == cbchannel or ctx.channel.id == bdchannel:
                try:
                    async with aiosqlite.connect('dbs/betting.db') as db:
                        cursor = await db.execute('SELECT * FROM bets WHERE side_name = ?', (side_name,))
                        bets = await cursor.fetchall()
                        if not bets:
                            e.title = f"📣 {side_name} won! 📣"
                            e.description = f"There are no bets placed on **{side_name}**, though!"
                            await ctx.send(embed=e)
                            return
                        cursor = await db.execute('SELECT * FROM sides WHERE side_name = ?', (side_name,))
                        winning_side = await cursor.fetchone()
                        if not winning_side:
                            e.title = "❌ Invalid Side Input ❌"
                            e.description = f"There is no side called **{side_name}**!"
                            await ctx.send(embed=e)
                            return
                        for bet_info in bets:
                            user_id, _, _, bet = bet_info
                            async with aiosqlite.connect('dbs/balance.db') as balance_db:
                                cursor = await balance_db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                                user_account = await cursor.fetchone()
                                if user_account:
                                    current_balance = user_account[1]
                                    user_share = bet * (1 / winning_side[1])
                                    user_winnings = bet * winning_side[1]
                                    total_winnings = user_winnings + bet
                                    new_balance = current_balance + total_winnings
                                    await balance_db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                                    await balance_db.commit()
                    e.title = f"📣 {side_name} won! 📣"
                    e.description = f"*All users who bet on* ***{side_name}*** *have been paid their winnings!*"
                    await ctx.send(embed=e)
                    async with aiosqlite.connect('dbs/betting.db') as db:
                        await db.execute('DELETE FROM sides')
                        await db.execute('DELETE FROM bets')
                        await db.commit()
                except Exception as e:
                    print(e)
            else:
                e.title = "❌ Incorrect Channel ❌"
                e.description = "This isn't the correct channel! Head to <#1177498679758827550> to use **CreateBet**!"
                await ctx.send(embed=e, ephemeral=True)
                return
        else:
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
            return

    def convert_duration(self, duration):
        pos = ['s', 'm', 'h', 'd']
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
        unit = duration[-1]
        if unit not in pos:
            return -1
        try:
            val = int(duration[:-1])
        except ValueError:
            return -1
        return timedelta(seconds=val * time_dict[unit])


async def setup(bot):
    await bot.add_cog(BettingCog(bot))