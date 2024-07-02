import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio

# Stores when the bot was started
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.launch_time = datetime.utcnow()

# General Commands Embed
ge = discord.Embed(color=0xff5f39)
ge.set_author(name="Bot Commands", icon_url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
ge.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
ge.add_field(
    name="📌 __General Commands__",
    value=f"> `Help`, `Info`, `Test`, `Ping`, `Suggest`, `Giveaway`, `FeeCalc`",
)

# Play Commands Embed
pe = discord.Embed(color=0xff5f39)
pe.set_author(name="Bot Commands", icon_url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
pe.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
pe.add_field(
    name="💸 __Game Commands__",
    value=f"> `Coinflip`, `DuelFlip`, `Slots`, `Crash`, `Buy`, `Out` \n> `Blackjack`, `Roulette`, `Sixes`, `Bet`",
)

# Account Commands Embed
ae = discord.Embed(color=0xff5f39)
ae.set_author(name="Bot Commands", icon_url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
ae.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
ae.add_field(
    name="🧾 __Account Commands__",
    value=f"> `CreateAccount`, `DeleteAccount`, `Balance`, `Pay`, `Baltop`",
)

# Help Menu Dropdown
class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General Commands",description="Help, Info, Test, Ping, Suggest, Giveaway +1 More", emoji="📌"),
            discord.SelectOption(label="Game Commands",description="Coinflip, DuelFlip, Slots, Crash, Buy, Out +3 More", emoji="💸"),
            discord.SelectOption(label="Account Commands",description="CreateAccount, DeleteAccount, Balance, Pay, Baltop", emoji="🧾"),
        ]
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self,interaction:discord.Interaction):
        if self.values[0] == "General Commands":
            await interaction.response.edit_message(embed=ge)
        if self.values[0] == "Game Commands":
            await interaction.response.edit_message(embed=pe)  
        if self.values[0] == "Account Commands":
            await interaction.response.edit_message(embed=ae) 
    
# DropdownView Class
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())      
        
# General Commands Class
class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.initialize_database() # Logging DB
        await self.bot.change_presence(activity=discord.Game(name="Helping RC Guests..."))
        await self.create_suggestion_table()

    async def initialize_database(self):
        self.db_conn = await aiosqlite.connect("dbs/logging.db")
    
    async def get_logging_channel(self, guild_id):
        async with self.db_conn.execute(
            "SELECT channel_id FROM logging_channels WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def create_suggestion_table(self):
        async with aiosqlite.connect("dbs/suggest.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS suggestion_channels (server_id INTEGER, channel_id INTEGER)")
            await db.commit()
    
    async def get_suggestion_channel(self, guild_id):
        async with aiosqlite.connect("dbs/suggest.db") as db:
            cursor = await db.execute("SELECT channel_id FROM suggestion_channels WHERE server_id = ?", (guild_id,))
            suggestion_channel_id = await cursor.fetchone()
        return self.bot.get_channel(suggestion_channel_id[0]) if suggestion_channel_id else None
    
    @commands.command()
    async def postverify(self, ctx):
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            e = discord.Embed(color=0xff5f39)
            e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png")
            e.description = "# __Rosewood Casino TOS__ \n ### Effective Date: October 18th, 2023 \n**Introduction** \n> *Welcome to Rosewood Casino! By clicking the verification button to participate in our casino, you agree to abide by the following Terms of Service. It's important to read and understand these terms before proceeding.* \n \n **1) Eligibility** \n > You must have a Java Minecraft Account and a Discord Account to use our services. By verifying, you confirm that you meet this requirement.  \n \n **2) Responsible Gaming** \n> Gambling should be done responsibly. Only wager what you can afford to lose. If you believe you may have a gambling problem, please seek assistance and consider self-exclusion options.   \n \n **3) Deposits and Withdrawals** \n> a. All deposits and withdrawals are final. \n> b. We are not responsible for any loss or damage to your account balance. \n> c. To withdraw money, you must have deposited money.  \n  \n **4) Fair Play** \n> a. We strive to ensure fairness in our games, but outcomes are determined by chance. \n> b. We do not guarantee winnings, and you may lose money.  \n \n **5)  Account Termination** \n> a. We may terminate or suspend your account for violations of these terms.  \n \n **7) Updates** \n> We may update these Terms of Service at any time. It's your responsibility to check for changes.  \n \n **8) Acceptance** \n> By clicking the verification button, you acknowledge that you have read and understood our Terms of Service and agree to abide by them. \n \n *If you have any questions, comments or concerns please let a Staff member know! Thank you!*"
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="✅ Accept TOS", custom_id="verify"))
            await ctx.send(embed=e, view=view)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)

    @commands.command()
    async def selfroles(self, ctx):
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            e = discord.Embed(color=0xff5f39)
            e.title = "🌹 Rosewood Self Roles 🌹"
            e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
            e.description = ":game_die: <@&1164594965905678346> - Get pinged when there's a live event \n:bell: <@&1169819033638539394> - Get pinged when there's a casino update \n:tada: <@&1173401429671673937> - Get pinged when there's a giveaway \n📰 <@&1177499276377600020> - Get pinged when there's a bet"
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="🎲 EventPings", custom_id="eventpings"))
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="🔔 UpdatePings", custom_id="updatepings"))
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="🎉 GiveawayPings", custom_id="giveawaypings"))
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="📰 BettingPings", custom_id="bettingpings"))
            await ctx.send(embed=e, view=view)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'verify':
                    guests_role = discord.utils.get(interaction.guild.roles, name="Guests")
                    if guests_role in interaction.user.roles:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🌹 Already Verified! 🌹"
                        e.description = "You have already accepted the Rosewood Casino TOS!"
                        await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        await interaction.user.add_roles(guests_role)
                        e = discord.Embed(color=0xff5f39)
                        e.title = "✨ You've been verified! ✨"
                        e.description = "Thank you for accepting the **Rosewood Casino TOS**! *You may now enter the casino!*"
                        await interaction.response.send_message(embed=e, ephemeral=True)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'eventpings':
                    event_role = discord.utils.get(interaction.guild.roles, name="EventPings")
                    if event_role in interaction.user.roles:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🎲 EventPings Role Removed! 🎲"
                        e.description = "You will no longer receive live event pings."
                        await interaction.user.remove_roles(event_role)
                        await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        await interaction.user.add_roles(event_role)
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🎲 EventPings Role Added! 🎲"
                        e.description = "You will now get pinged anytime there's a live event!"
                        await interaction.response.send_message(embed=e, ephemeral=True)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'updatepings':
                    update_role = discord.utils.get(interaction.guild.roles, name="UpdatePings")
                    if update_role in interaction.user.roles:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🔔 UpdatePings Role Removed! 🔔"
                        e.description = "You will no longer receive casino update pings."
                        await interaction.user.remove_roles(update_role)
                        await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        await interaction.user.add_roles(update_role)
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🔔 UpdatePings Role Added! 🔔"
                        e.description = "You will now get pinged anytime there's a casino update!"
                        await interaction.response.send_message(embed=e, ephemeral=True)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'giveawaypings':
                    giveaway_role = discord.utils.get(interaction.guild.roles, name="GiveawayPings")
                    if giveaway_role in interaction.user.roles:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🎉 GiveawayPings Role Removed! 🎉"
                        e.description = "You will no longer receive casino giveaway pings."
                        await interaction.user.remove_roles(giveaway_role)
                        await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        await interaction.user.add_roles(giveaway_role)
                        e = discord.Embed(color=0xff5f39)
                        e.title = "🎉 UpdatePings Role Added! 🎉"
                        e.description = "You will now get pinged anytime there's a giveaway!"
                        await interaction.response.send_message(embed=e, ephemeral=True)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'bettingpings':
                    betting_role = discord.utils.get(interaction.guild.roles, name="BettingPings")
                    if betting_role in interaction.user.roles:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "📰 BettingPings Role Removed! 📰"
                        e.description = "You will no longer receive casino betting pings."
                        await interaction.user.remove_roles(betting_role)
                        await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        await interaction.user.add_roles(betting_role)
                        e = discord.Embed(color=0xff5f39)
                        e.title = "📰 BettingPings Role Added! 📰"
                        e.description = "You will now get pinged anytime there's a bet!"
                        await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as e:
            print(e)
    
    @commands.hybrid_command(description="Set the suggestion channel for the server")
    async def setsuggest(self, ctx, channel: discord.TextChannel):
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ['yes', 'no']
            await self.create_suggestion_table()
            await ctx.send(f"Is {channel.mention} the correct channel? [Yes/No]")
            try:
                reply = await self.bot.wait_for('message', check=check, timeout=30)
                if reply.content.lower() == 'yes':
                    async with aiosqlite.connect("dbs/suggest.db") as db:
                        await db.execute("DELETE FROM suggestion_channels WHERE server_id = ?", (ctx.guild.id,))
                        await db.execute("INSERT INTO suggestion_channels (server_id, channel_id) VALUES (?, ?)", (ctx.guild.id, channel.id))
                        await db.commit()
                    await ctx.send(f"Suggestion channel has been set to {channel.mention}")
                else:
                    await ctx.send("Please retry the command and mention the correct channel!")
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Suggestion channel setting cancelled.")
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)

    @commands.command()
    async def posttutorial(self, ctx):
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            e = discord.Embed(color=0xff5f39)
            e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png")
            e.description = "# Casino Tutorials \n *This is a list and explanation of every (publicly available) command and tutorials!* \n \n## __How To Deposit__ \n**1)** `/pay` your deposit amount to `GamingDerp` or `bogie95` \n**2)** Screenshot and send the pic in your ticket \n**3)** Ping the owner you paid \n \nor \n \n**1)** Pay with [**Aegis Bank**](https://discord.gg/dTZ43q7B35) and [**Crimson Bank**](https://discord.gg/RbfsDrtvhV) \n> [**Aegis:**](https://discord.gg/dTZ43q7B35) 1083 \n> [**Crimson:**](https://discord.gg/RbfsDrtvhV) 10066 \n## __How To Withdraw__ \n**1)** Ping one of the owners \n**2)** Request your withdrawal amount \n> **Withdrawal Limit:** $1,000,000 (per withdrawal) \n> **Withdrawal Fee:** 2% \n## __General Commands__ \n📌 `Help` - Shows the bot's help menu \n📌 `Info` - Shows information about the bot \n📌 `Test` - Tests if the bot is online \n📌 `Ping` - Shows your ping \n📌 `Suggest` - Sends your suggestion to <#1169813614421627011>\n## __Game Commands__ \n💸 `Coinflip` - Flips a coin against the House \n💸 `DuelFlip` - Challenge another user to a coinflip \n💸 `Slots` - Plays a game of slots \n💸 `Crash` - Starts a game of crash \n💸 `Buy` - Joins the game of crash \n💸 `Out` - Leaves the game of crash \n💸 `Blackjack` - Plays a game of blackjack \n💸 `Roulette` - Plays a game of roulette \n💸`Bet` - Buys into an ongoing bet \n## __Account Commands__ \n🧾 `CreateAccount` - Creates a Rosewood Casino Account \n🧾 `DeleteAccount` - Deletes your Rosewood Casino Account \n🧾 `Balance` - Shows your account's balance \n🧾 `Pay` - Pays another user \n🧾 `Baltop` - Lists the top 10 users with the highest balance \n \n *If you have any questions, comments or concerns please let a Staff member know! Thank you!*"
            await ctx.send(embed=e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)

    @commands.hybrid_command(description="Sends the bots help menu")
    async def help(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["help"]:
            return
        e = discord.Embed(color=0xff5f39)
        e.set_author(name="Bot Commands", icon_url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
        e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
        e.add_field(
            name="✧ __Command Menus__",
            value=f"> 📌 General"
                  f"\n> 💸 Games"
                  f"\n> 🧾 Account",
        )
        view = DropdownView()
        await ctx.send(embed=e, view=view)

    @commands.hybrid_command(description="Sends information about the bot")
    async def info(self, ctx):
        try:
            if ctx.prefix == "!" and ctx.invoked_with in ["info"]:
                return
            logging_channel_id = await self.get_logging_channel(ctx.guild.id)
            logging_channel = self.bot.get_channel(logging_channel_id)
            suggestion_channel = await self.get_suggestion_channel(ctx.guild.id)
            total_lines = 24
            cog_directory = "./cogs"
            for filename in os.listdir(cog_directory):
                if filename.endswith(".py"):
                    with open(os.path.join(cog_directory, filename), "r") as file:
                        lines = file.readlines()
                        non_empty_lines = [line.strip() for line in lines if line.strip()]
                        total_lines += len(non_empty_lines)
            member_count = len(ctx.guild.members) # includes bots
            true_member_count = len([m for m in ctx.guild.members if not m.bot])
            delta_uptime = datetime.utcnow() - bot.launch_time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="Bot Information", icon_url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
            e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
            e.add_field(
                name="✧ __Server__",
                value=f"> **Suggestion:** {suggestion_channel.mention if suggestion_channel else 'None'}"
		      f"\n> **Logging:** {logging_channel.mention if logging_channel else 'None'}",
                inline=False
            )
            e.add_field(
                name="✧ __Statistics__",
                value=f"> **Commands:** [22]"
	                  f"\n> **Code:** {total_lines} Lines"
		          f"\n> **Ping:** {round(self.bot.latency * 1000)}ms"
		          f"\n> **Guests:** {true_member_count}"
        	          f"\n> **Uptime:** {days}**d** {hours}**h** {minutes}**m** {seconds}**s**",
                inline=False
            )
            e.add_field(
                name="✧ __Credits__",
                value=f"> **Dev:** `gamingderp`",
                inline=False
            )
            e.set_footer(text=f"Requested by {ctx.author}")
            e.timestamp = datetime.utcnow()
            await ctx.send(embed=e)
        except Exception as e:
            print(e)
    
    @commands.hybrid_command(description="Test if the bot is up")
    async def test(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["test"]:
            return
        await ctx.send("I'm up! <a:DerpPet:1164821123029016596>")

    @commands.hybrid_command(description="Sends your ping")
    async def ping(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["ping"]:
            return
        e = discord.Embed(color=0xff5f39)
        e.add_field(
            name="📶 Ping",
            value=f"Your ping is **{round(self.bot.latency * 1000)}**ms",
    	    inline=False
        )
        await ctx.send(embed=e)
    
    @commands.hybrid_command(description="Create a poll!")
    async def poll(self, ctx, question:str, option1:str=None, option2:str=None, option3:str=None, option4:str=None, option5:str=None):
        if ctx.prefix == "!" and ctx.invoked_with in ["poll"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            options = [option1, option2, option3, option4, option5]
            options = [option for option in options if option is not None]
            emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]      
            if not options:
                await ctx.send("Please provide at least two options for the poll.")
                return
            if len(options) > 5:
                await ctx.send("You can only have up to 5 options in the poll.")
                return       
            e = discord.Embed(color=0xff5f39)
            e.title = f"📊 **{question}**"
            description_text = ""
            for i, option in enumerate(options):
                description_text += f"\n{emoji_list[i]} {option}"
            e.description = description_text
            msg = await ctx.send(embed=e)
            for i in range(len(options)):
                await msg.add_reaction(emoji_list[i])
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)
    
    @commands.hybrid_command(description="Make a suggestion")
    async def suggest(self, ctx, *, suggestion):
        if ctx.prefix == "!" and ctx.invoked_with in ["suggest"]:
            return
        try:
            await self.create_suggestion_table()
            suggestion_channel = await self.get_suggestion_channel(ctx.guild.id)
            if suggestion_channel:
                se = discord.Embed(color=0xff5f39)
                se.set_author(name=f"Suggested by {ctx.author}")
                se.set_thumbnail(url=ctx.author.avatar.url)
                se.description = suggestion
                if ctx.message.attachments:
                    attachment_url = ctx.message.attachments[0].url
                    se.set_image(url=attachment_url)
                se.timestamp = datetime.utcnow()
                vote = await suggestion_channel.send(embed=se)
                for emoji in ["👍", "🤷‍♂️", "👎"]:
                    await vote.add_reaction(emoji)
                await ctx.send(f"Your suggestion has been added!")
            else:
                await ctx.send("No suggestion channel set!")
        except Exception as e:
            print(e)

    @commands.hybrid_command(description = "Calculate the fee of a withdrawal | RC Fee: 2%")
    async def feecalc(self, ctx, amount: float):
        if ctx.prefix == "!" and ctx.invoked_with in ["feecalc"]:
            return
        try:
            fee = 0.02 * amount
            amount_after_fee = amount - fee
            formatted_amount = "${:,.2f}".format(amount)
            formatted_amount_after_fee = "${:,.2f}".format(amount_after_fee)
            formatted_fee = "${:,.2f}".format(fee)
            e = discord.Embed(color=0xff5f39)
            e.title = "🧮 Fee Calculator 🧮"
            e.add_field(name="Input Amount", value=f"💰 {formatted_amount}", inline=False)
            e.add_field(name="Fee Percent", value=f"📑 2%", inline=False)
            e.add_field(name="Fee Amount", value=f"⚙️ {formatted_fee}", inline=False)
            e.add_field(name="After Fee Amount", value=f"💰 {formatted_amount_after_fee}", inline=False)
            await ctx.send(embed=e, ephemeral=True)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
