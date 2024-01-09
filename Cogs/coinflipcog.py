import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

class CoinflipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_state = {}

    @commands.hybrid_command(description="Play a game of coinflip")
    async def coinflip(self, ctx, bet: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["coinflip"]:
            return
        cfchannel = 1163620107281502248
        bdchannel = 1163616023073783938
        if ctx.channel.id == cfchannel or ctx.channel.id == bdchannel:
            try:
                min_bet = 25
                max_bet = 25000
                e = discord.Embed(color=0xff5f39)
                if bet < min_bet:
                    e.title = "💰 Minimum Bet 💰"
                    e.description = "The minimum bet for **Coinflip** is **$25**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if bet > max_bet:
                    e.title = "💰 Maximum Bet 💰"
                    e.description = "The maximum bet for **Coinflip** is **$25,000**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                        user_account = await cursor.fetchone()
                e = discord.Embed(color=0xff5f39)
                if not user_account:
                    e.title = "❓ Account Not Found ❓"
                    e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                account_balance = user_account[1]
                if bet > account_balance:
                    formatted_bet = "${:,.2f}".format(bet)
                    e.title = "⛔️ Insufficient Balance ⛔️"
                    e.description = f"You are unable to bet **{formatted_bet}**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                result = "Heads" if random.randint(1, 100) <= 50 else "Tails"
                winnings = 0
                if result == "Heads":
                    winnings = bet * 2
                new_balance = account_balance - bet + winnings
                async with aiosqlite.connect('dbs/balance.db') as db:
                    await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ?', (new_balance, user_id))
                    await db.commit()
                if result == "Heads":
                    formatted_winnings = "${:,.2f}".format(winnings)
                    e.title = "🔰 Heads! 🔰"
                    e.set_image(url="https://media.discordapp.net/attachments/1163615932489416804/1164754025477066876/heads.png?ex=65445cb7&is=6531e7b7&hm=4da1f100b24a165c1d4104bb40dea7bcbbbd37ac53bf7def6f7a964c3cdd81b4&=")
                    await ctx.send(embed=e, content=f"{ctx.author.mention} won **{formatted_winnings}**! 🎉")
                else:
                    e.title = "🔰 Tails! 🔰"
                    e.set_image(url="https://media.discordapp.net/attachments/1163615932489416804/1164754038936576150/tails.png?ex=65445cba&is=6531e7ba&hm=3f332601a3785f2a93a756f32e27c33d7ea6fb9ee08119e467e1991d16ab47fb&=")
                    await ctx.send(embed=e)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1163620107281502248> to use **Coinflip**!"
            await ctx.send(embed=e, ephemeral=True)
            return

    @commands.hybrid_command(description="Challenge another user to a duelflip")
    async def duelflip(self, ctx, challenged_user: discord.User, bet: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["duelflip"]:
            return
        cfchannel = 1163620107281502248
        bdchannel = 1163616023073783938
        if ctx.channel.id == cfchannel or ctx.channel.id == bdchannel:
            try:
                e = discord.Embed(color=0xff5f39)
                user_id = ctx.author.id
                if bet <= 25:
                    e.title = "💰 Minimum Bet 💰"
                    e.description = "The minimum bet for **DuelFlip** is **$25**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                async with aiosqlite.connect('dbs/balance.db') as db:
                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                        user_account = await cursor.fetchone()
                    if not user_account:
                        e.title = "❓ Account Not Found ❓"
                        e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    account_balance = user_account[1]
                    challenged_user_id = challenged_user.id
                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (challenged_user_id,)) as cursor:
                        challenged_user_account = await cursor.fetchone()
                    if not challenged_user_account:
                        e.title = "❓  Account Not Found ❓"
                        e.description = f"That user doesn't have a ***Rosewood Casino*** account!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    challenged_user_balance = challenged_user_account[1]
                    if bet > account_balance:
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"You are unable to bet **${bet}**."
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    if bet > challenged_user_balance:
                        e.title = "⛔️ Insufficient Balance ⛔️"
                        e.description = f"That user is unable to accept the duelflip challenge due to an insufficient balance."
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    await db.commit()
                    challenger = ctx.author
                    challenger_id = challenger.id
                    formatted_bet = "${:,.2f}".format(bet)
                    if challenged_user.id == challenger_id:
                        e.title = "❌ Duel Cancelled ❌"
                        e.description = "You can't challenge yourself to a duelflip!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    e = discord.Embed(
                        title="⚔️ DuelFlip Challenge ⚔️",
                        description=f"{challenger.mention} has challenged {challenged_user.mention} to a duelflip for **{formatted_bet}**!\n\n*Do you accept the challenge?*",
                        color=0xff5f39,
                    )
                    accept_button = discord.ui.Button(
                        style=discord.ButtonStyle.green,
                        label="✅ Accept",
                        custom_id="accept_duel",
                    )
                    deny_button = discord.ui.Button(
                        style=discord.ButtonStyle.red,
                        label="❌ Deny",
                        custom_id="deny_duel",
                    )
                    view = discord.ui.View()
                    view.add_item(accept_button)
                    view.add_item(deny_button)
                    challenge_message = await ctx.send(embed=e, view=view, content=f"{challenged_user.mention} has been challenged!")
                    self.game_state[challenge_message.id] = {
                        "challenger_id": challenger_id,
                        "challenged_user_id": challenged_user.id,
                        "bet": bet,
                    }
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1163620107281502248> to use **DuelFlip**!"
            await ctx.send(embed=e, ephemeral=True)
            return

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.type != discord.InteractionType.component:
                return
            game_data = self.game_state.get(interaction.message.id)
            if not game_data:
                return 
            if interaction.type == discord.InteractionType.component and game_data:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    if interaction.data['custom_id'] == 'accept_duel':
                        challenged_user_id = game_data["challenged_user_id"]
                        challenger_id = game_data["challenger_id"]
                        if interaction.user.id == challenged_user_id:
                            bet = game_data["bet"]
                            challenger = self.bot.get_user(challenger_id)
                            challenged_user = self.bot.get_user(challenged_user_id)
                            user_id = challenger_id
                            async with aiosqlite.connect('dbs/balance.db') as db:
                                async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)) as cursor:
                                    user_account = await cursor.fetchone()
                                    account_balance = user_account[1]
                                    challenged_user_id = challenged_user.id
                                    async with db.execute('SELECT * FROM accounts WHERE user_id = ?', (challenged_user_id,)) as cursor:
                                        challenged_user_account = await cursor.fetchone()
                                        challenged_user_balance = challenged_user_account[1]
                                        e = discord.Embed(color=0xff5f39)
                                        if bet > account_balance:
                                            e.title = "⛔️ Insufficient Balance ⛔️"
                                            e.description = f"You are unable to bet **${bet}**."
                                            await interaction.response.send_message(embed=e, ephemeral=True)
                                            return
                                        if bet > challenged_user_balance:
                                            e.title = "⛔️ Insufficient Balance ⛔️"
                                            e.description = f"You are unable to accept the duelflip challenge!"
                                            await interaction.response.send_message(embed=e, ephemeral=True)
                                            return
                            challenger = self.bot.get_user(challenger_id)
                            challenged_user = self.bot.get_user(challenged_user_id)
                            async with aiosqlite.connect('dbs/balance.db') as db:
                                result = "Heads" if random.randint(1, 100) <= 50 else "Tails"
                                if result == "Heads":
                                    winnings = bet
                                    formatted_winnings = "${:,.2f}".format(winnings)
                                    await db.execute('UPDATE accounts SET account_balance = account_balance - ? WHERE user_id = ?', (winnings, challenged_user_id))
                                    await db.commit()
                                    await db.execute('UPDATE accounts SET account_balance = account_balance + ? WHERE user_id = ?', (bet, challenger_id))
                                    await db.commit()
                                    e = discord.Embed(
                                        title="⚔️ DuelFlip ⚔️",
                                        description=f"{challenger.mention} won **{formatted_winnings}**! 🎉",
                                        color=0xff5f39,
                                    )
                                    e.set_image(url="https://media.discordapp.net/attachments/1163615932489416804/1164754025477066876/heads.png?ex=65445cb7&is=6531e7b7&hm=4da1f100b24a165c1d4104bb40dea7bcbbbd37ac53bf7def6f7a964c3cdd81b4&=")
                                else:
                                    winnings = bet
                                    formatted_winnings = "${:,.2f}".format(winnings)
                                    await db.execute('UPDATE accounts SET account_balance = account_balance + ? WHERE user_id = ?', (winnings, challenged_user_id))
                                    await db.commit()
                                    await db.execute('UPDATE accounts SET account_balance = account_balance - ? WHERE user_id = ?', (bet, challenger_id))
                                    await db.commit()
                                    e = discord.Embed(
                                        title="⚔️ DuelFlip ⚔️",
                                        description=f"{challenged_user.mention} won **{formatted_winnings}**! 🎉",
                                        color=0xff5f39,
                                    )
                                    e.set_image(url="https://media.discordapp.net/attachments/1163615932489416804/1164754038936576150/tails.png?ex=65445cba&is=6531e7ba&hm=3f332601a3785f2a93a756f32e27c33d7ea6fb9ee08119e467e1991d16ab47fb&=")
                                view = discord.ui.View()
                                await interaction.response.send_message(embed=e, view=view)
                                del self.game_state[interaction.message.id]
                        else:
                            e = discord.Embed(
                                title="❌ You Weren't Challenged! ❌",
                                description="You are not the challenged user!",
                                color=0xff5f39,
                            )
                            await interaction.response.send_message(embed=e, ephemeral=True)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'deny_duel':
                    challenged_user_id = game_data["challenged_user_id"]
                    if interaction.user.id == challenged_user_id:
                        challenged_user = self.bot.get_user(challenged_user_id)
                        del self.game_state[interaction.message.id]
                        await interaction.response.send_message(content=f"{challenged_user.mention} denied the duelflip challenge!")
                else:
                    e = discord.Embed(
                        title="❌ You Weren't Challenged! ❌",
                        description="You are not the challenged user!",
                        color=0xff5f39,
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CoinflipCog(bot))