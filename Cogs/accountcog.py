import aiosqlite
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import asyncio

# Account Deletion Embed
de = discord.Embed(color=0xff5f39)
de.title = "📛 Account Deleted 📛"
de.description = "Your ***Rosewood Casino*** account has been deleted!"

# Command Cancellation Embed
ce = discord.Embed(color=0xff5f39)
ce.title = "❌ Command Cancelled ❌"
ce.description = "Account deletion command has been cancelled!"

# Account Commands Class
class AccountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.setup_database()
        await self.bot.tree.sync()

    async def setup_database(self):
        async with aiosqlite.connect('dbs/balance.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS accounts (
                account_number INTEGER PRIMARY KEY,
                account_balance REAL,
                user_ign TEXT,
                user_id INTEGER
            )''')
            await db.execute('CREATE TABLE IF NOT EXISTS account_counter (last_account_number INTEGER)')
            await db.commit()
            cursor = await db.execute('SELECT last_account_number FROM account_counter')
            if not await cursor.fetchone():
                await db.execute('INSERT INTO account_counter (last_account_number) VALUES (?)', (1000,))
                await db.commit()

    @commands.hybrid_command(description="Create a Rosewood Casino Account")
    async def createaccount(self, ctx, user_ign: str):
        if ctx.prefix == "!" and ctx.invoked_with in ["createaccount"]:
            return
        try:
            category_one = 1163648798426415114
            category_two = 1173535177838968923
            category = ctx.channel.category
            if category and category.id == category_one or category and category.id == category_two:
                user_id = ctx.author.id
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                    existing_account = await cursor.fetchone()
                    e = discord.Embed(color=0xff5f39)
                    a = discord.Embed(color=0xff5f39)
                    if existing_account:
                        e.title = "🔍 Account Already Exists 🔍"
                        e.description = f"Account for **{ctx.author.display_name}** already exists."
                        await ctx.send(embed=e)
                    else:
                        cursor = await db.execute('SELECT last_account_number FROM account_counter')
                        last_account_number_result = await cursor.fetchone()
                        last_account_number = last_account_number_result[0]
                        new_account_number = last_account_number + 1
                        await db.execute('INSERT INTO accounts (account_number, account_balance, user_ign, user_id) VALUES (?, ?, ?, ?)', (new_account_number, 0.0, user_ign, user_id))
                        await db.execute('UPDATE account_counter SET last_account_number = ?', (new_account_number,))
                        await db.commit()
                        e.title = "🍻 Account Created 🍻"
                        e.description = f"A ***Rosewood Casino*** account for **{user_ign}** has been created!"
                        e.add_field(
                            name="Account Number",
                            value=f"📋 {new_account_number}",
                            inline=False
                        )
                        e.add_field(
                            name="User IGN",
                            value=f"📌 {user_ign}",
                            inline=False
                        )
                        await ctx.send(embed=e)
                        account_role = discord.utils.get(ctx.guild.roles, name="Account Holder")
                        await ctx.author.add_roles(account_role)
                        message = ctx.message
                        message_datetime = message.created_at
                        timestamp = int(datetime.timestamp(message_datetime))
                        channel_id = 1164562313022554272
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            a.title = "✅ Account Created ✅"
                            a.add_field(
                                name="Account Number",
                                value=f"📋 {new_account_number}",
                                inline=False
                            )
                            a.add_field(
                                name="User IGN",
                                value=f"📌 {user_ign}",
                                inline=False
                            )
                            a.add_field(
                                name="Timestamp",
                                value=f"⏰ <t:{timestamp}:f>",
                                inline=False
                            )
                            await channel.send(embed=a)
                        else:
                            print(f"Channel with ID {channel_id} not found.")
            else:
                e = discord.Embed(color=0xff5f39)
                e.title = "❓ Account Not Found ❓"
                e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                await ctx.send(embed=e, ephemeral=True)
                return  
        except Exception as e:
            print(e)

    @commands.hybrid_command(description="Delete your Rosewood Casino account")
    async def deleteaccount(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["deleteaccount"]:
            return
        user_id = ctx.author.id
        async with aiosqlite.connect('dbs/balance.db') as db:
            cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
            existing_account = await cursor.fetchone()
        if not existing_account:
            e = discord.Embed(color=0xff5f39)
            e.title = "❓ Account Not Found ❓"
            e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
            await ctx.send(embed=e, ephemeral=True)
            return
        e = discord.Embed(color=0xff5f39)
        e.title = "🛑 Delete Casino Account 🛑"
        e.set_thumbnail(url="https://media.discordapp.net/attachments/1163615932489416804/1163640941018624050/RosewoodLogo.png?ex=65405013&is=652ddb13&hm=211bd6a1ddc6e4d0587d0d99962b228d50d802a18395ffb38828752e5db12fb9&=")
        e.description = "Are you sure you want to delete your ***Rosewood Casino*** account?"
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.success, label="✅", custom_id="confirm"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.danger, label="❌", custom_id="cancel"))
        message = await ctx.send(embed=e, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'confirm':
                    user_id = interaction.user.id
                    account_role = discord.utils.get(interaction.guild.roles, name="Account Holder")
                    await interaction.user.remove_roles(account_role)
                    async with aiosqlite.connect('dbs/balance.db') as db:
                        cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                        deleted_account = await cursor.fetchone()
                        if deleted_account:
                            account_number, account_balance, user_ign, _ = deleted_account
                            formatted_balance = "${:,.2f}".format(account_balance)
                            await db.execute('DELETE FROM accounts WHERE user_id = ?', (interaction.user.id,))
                            await db.commit()
                            await interaction.response.edit_message(embed=de, view=None)
                            channel_id = 1164562313022554272
                            channel = self.bot.get_channel(channel_id)
                            message = interaction.message
                            message_datetime = message.created_at
                            timestamp = int(datetime.timestamp(message_datetime))
                            if channel:
                                z = discord.Embed(color=0xff5f39)
                                z.title = "📛 Account Deleted 📛"
                                z.add_field(
                                    name="Account Number", 
                                    value=f"📋 {account_number}",
                                    inline=False
                                )
                                z.add_field(
                                    name="User IGN", 
                                    value=f"📌 {user_ign}",
                                    inline=False
                                )
                                z.add_field(
                                    name="Balance", 
                                    value=f"💰 {formatted_balance}",
                                    inline=False
                                )
                                z.add_field(
                                    name="Timestamp",
                                    value=f"⏰ <t:{timestamp}:f>",
                                    inline=False
                                )
                                await channel.send(embed=z)
                            else:
                                print(f"Channel with ID {channel_id} not found.")
                        else:
                            await interaction.response.send_message(embed=ce)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'cancel':
                    await interaction.response.edit_message(embed=ce, view=None)
        except Exception as e:
            print(e)
    
    @commands.hybrid_command(description="Forcefully delete a Rosewood Casino account")
    async def forcedelete(self, ctx, account_number: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["forcedelete"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
                    existing_account = await cursor.fetchone()
                    if existing_account:
                        account_number, account_balance, user_ign, _ = existing_account
                        formatted_balance = "${:,.2f}".format(account_balance)
                        await db.execute('DELETE FROM accounts WHERE account_number = ?', (account_number,))
                        await db.commit()
                        e = discord.Embed(color=0xff5f39)
                        e.title = "⚠️ Account Deleted ⚠️"
                        e.description = f"Account **{account_number}** has been forcefully deleted!"
                        await ctx.send(embed=e)
                        channel_id = 1164562313022554272
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            e = discord.Embed(color=0xff5f39)
                            e.title = "📛 Account Deleted 📛"
                            e.add_field(
                                name="Account Number", 
                                value=f"📋 {account_number}",
                                inline=False
                            )
                            e.add_field(
                                name="User IGN", 
                                value=f"📌 {user_ign}",
                                inline=False
                            )
                            e.add_field(
                                name="Balance", 
                                value=f"💰 {formatted_balance}",
                                inline=False
                            )
                            await channel.send(embed=e)
                        else:
                            print(f"Channel with ID {channel_id} not found.")
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = f"Account **{account_number}** does not exist."
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
    
    @commands.hybrid_command(description="Edit a Casino Account Holder's Account Number")
    async def editnumber(self, ctx, current_account_number: int, new_account_number: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["editnumber"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute("SELECT * FROM accounts WHERE account_number = ?", (current_account_number,))
                    user_account = await cursor.fetchone()
                    if user_account:
                        await db.execute("UPDATE accounts SET account_number = ? WHERE account_number = ?", (new_account_number, current_account_number))
                        await db.commit()
                        e = discord.Embed(color=0xff5f39)
                        e.title = "⚙️ Account Number Updated ⚙️"
                        e.add_field(
                            name="Current Account Number",
                            value=f"📋 {current_account_number}",
                            inline=False
                        )
                        e.add_field(
                            name="New Account Number",
                            value=f"📌 {new_account_number}",
                            inline=False
                        )
                        await ctx.send(embed=e)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = f"Account **{current_account_number}** does not exist."
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)

    @commands.hybrid_command(description="Edit a Casino Account Holder's IGN")
    async def editign(self, ctx, account_number: int, new_ign: str):
        if ctx.prefix == "!" and ctx.invoked_with in ["editign"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute("SELECT * FROM accounts WHERE account_number = ?", (account_number,))
                    user_account = await cursor.fetchone()
                    if user_account:
                        await db.execute("UPDATE accounts SET user_ign = ? WHERE account_number = ?", (new_ign, account_number))
                        await db.commit()
                        e = discord.Embed(color=0xff5f39)
                        e.title = "⚙️ Account IGN Updated ⚙️"
                        e.add_field(
                            name="Account Number",
                            value=f"📋 {account_number}",
                            inline=False
                        )
                        e.add_field(
                            name="New IGN",
                            value=f"📌 {new_ign}",
                            inline=False
                        )
                        await ctx.send(embed=e)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = f"Account **{account_number}** does not exist."
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)

    @commands.hybrid_command(description="Check the balance of your Casino Account")
    async def balance(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["balance"]:
            return
        try:
            user_id = ctx.author.id
            async with aiosqlite.connect('dbs/balance.db') as db:
                cursor = await db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
                account_info = await cursor.fetchone()
                e = discord.Embed(color=0xff5f39)
                if account_info:
                    account_number, account_balance, user_ign, _ = account_info
                    formatted_balance = "${:,.2f}".format(account_balance)
                    e.title = "⚖️ Account Balance ⚖️"
                    e.add_field(
                        name="Account Number",
                        value=f"📋 {account_number}",
                        inline=False
                    )
                    e.add_field(
                        name="Account Balance",
                        value=f"💰 {formatted_balance}",
                        inline=False
                    )
                    e.add_field(
                        name="User IGN",
                        value=f"📌 {user_ign}",
                        inline=False
                    )
                    await ctx.send(embed=e, ephemeral=True)
                else:
                    e.title = "❓ Account Not Found ❓"
                    e.description = "You don't have a ***Rosewood Casino*** account! Head to <#1163647875423674471> to create one!"
                    await ctx.send(embed=e, ephemeral=True)
        except Exception as e:
            print(e)

    @commands.hybrid_command(description="Deposit money into a Rosewood Casino account")
    async def deposit(self, ctx, account_number: int, amount: float):
        if ctx.prefix == "!" and ctx.invoked_with in ["deposit"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
                    account_info = await cursor.fetchone()
                    if account_info:
                        account_number, account_balance, user_ign, _ = account_info
                        new_balance = account_balance + amount
                        formatted_balance = "${:,.2f}".format(new_balance)
                        formatted_amount = "${:,.2f}".format(amount)
                        await db.execute('UPDATE accounts SET account_balance = ? WHERE account_number = ?', (new_balance, account_number))
                        await db.commit()
                        message = ctx.message
                        message_datetime = message.created_at
                        timestamp = int(datetime.timestamp(message_datetime))
                        e = discord.Embed(color=0xff5f39)
                        e.title = "💸 Deposit Completed 💸"
                        e.add_field(
                            name="Account Number",
                            value=f"📋 {account_number}",
                            inline=False
                        )
                        e.add_field(
                            name="Deposit Amount",
                            value=f"💎 {formatted_amount}",
                            inline=False
                        )
                        e.add_field(
                            name="Balance",
                            value=f"💰 {formatted_balance}",
                            inline=False
                        )
                        e.add_field(
                            name="User IGN",
                            value=f"📌 {user_ign}",
                            inline=False
                        )
                        e.add_field(
                            name="Timestamp",
                            value=f"⏰ <t:{timestamp}:f>",
                            inline=False
                        )
                        await ctx.send(embed=e)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = f"Account **{account_number}** does not exist."
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
    
    @commands.hybrid_command(description="Withdraw money from a Rosewood Casino Account")
    async def withdraw(self, ctx, account_number: int, amount: float):
        if ctx.prefix == "!" and ctx.invoked_with in ["withdraw"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    cursor = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
                    account_info = await cursor.fetchone()
                    if account_info:
                        account_number, account_balance, user_ign, _ = account_info
                        fee = 0.02 * amount
                        amount_after_fee = amount - fee
                        if amount <= account_balance:
                            new_balance = account_balance - amount
                            formatted_balance = "${:,.2f}".format(new_balance)
                            formatted_amount = "${:,.2f}".format(amount_after_fee)
                            formatted_fee = "${:,.2f}".format(fee)
                            await db.execute('UPDATE accounts SET account_balance = ? WHERE account_number = ?', (new_balance, account_number))
                            await db.commit()
                            message = ctx.message
                            message_datetime = message.created_at
                            timestamp = int(datetime.timestamp(message_datetime))
                            e = discord.Embed(color=0xff5f39)
                            e.title = "💸 Withdraw Completed 💸"
                            e.add_field(
                                name="Account Number",
                                value=f"📋 {account_number}",
                                inline=False
                            )
                            e.add_field(
                                name="Withdraw Amount",
                                value=f"💎 {formatted_amount}",
                                inline=False
                            )
                            e.add_field(
                                name="Fee",
                                value=f"📑 {formatted_fee}",
                                inline=False
                            )
                            e.add_field(
                                name="Balance",
                                value=f"💰 {formatted_balance}",
                                inline=False
                            )
                            e.add_field(
                                name="User IGN",
                                value=f"📌 {user_ign}",
                                inline=False
                            )
                            e.add_field(
                                name=f"Timestamp",
                                value=f"⏰ <t:{timestamp}:f>",
                                inline=False
                            )
                            await ctx.send(embed=e)
                        else:
                            e = discord.Embed(color=0xff5f39)
                            e.title = "⛔️ Insufficient Balance ⛔️"
                            e.description = f"Account **{account_number}** is not able to withdraw **${amount}**!"
                            e.add_field(
                                name="Balance",
                                value=f"💰 ${account_balance}",
                            )
                            await ctx.send(embed=e)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = f"Account **{account_number}** does not exist!"
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
    
    @commands.hybrid_command(description="Transfer funds from one Rosewood Casino Account to another")
    async def pay(self, ctx, from_account_number: int, to_account_number: int, amount: float):
        if ctx.prefix == "!" and ctx.invoked_with in ["pay"]:
            return
        try:
            user_id = ctx.author.id
            async with aiosqlite.connect('dbs/balance.db') as db:
                from_account = await db.execute('SELECT * FROM accounts WHERE user_id = ? AND account_number = ?', (user_id, from_account_number))
                to_account = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (to_account_number,))
                from_account_info = await from_account.fetchone()
                to_account_info = await to_account.fetchone()
                formatted_amount = "${:,.2f}".format(amount)
                if not from_account_info:
                    e = discord.Embed(color=0xff5f39)
                    e.title = "❌ Invalid Account Number ❌"
                    e.description = f"Account **{from_account_number}** does not exist or you do not own it."
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if not to_account_info:
                    e = discord.Embed(color=0xff5f39)
                    e.title = "❌ Invalid Account Number ❌"
                    e.description = f"Account **{to_account_number}** does not exist."
                    await ctx.send(embed=e, ephemeral=True)
                    return
                from_account_balance = from_account_info[1]
                if from_account_balance < amount:
                    e = discord.Embed(color=0xff5f39)
                    e.title = "⛔️ Insufficient Balance ⛔️"
                    e.description = f"Account **{from_account_number}** is not able to send **{formatted_amount}**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if amount <= 0:
                    e = discord.Embed(color=0xff5f39)
                    e.title = "❌ Invalid Amount ❌"
                    e.description = f"You cannot send **${formatted_amount}**! That's not a positive number!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if from_account_number == to_account_number:
                    e = discord.Embed(color=0xff5f39)
                    e.title = "❌ Invalid Account ❌"
                    e.description = f"You cannot send money to yourself!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                new_from_balance = from_account_balance - amount
                new_to_balance = to_account_info[1] + amount
                await db.execute('UPDATE accounts SET account_balance = ? WHERE user_id = ? AND account_number = ?', (new_from_balance, user_id, from_account_number))
                await db.execute('UPDATE accounts SET account_balance = ? WHERE account_number = ?', (new_to_balance, to_account_number))
                await db.commit()
                message = ctx.message
                message_datetime = message.created_at
                timestamp = int(datetime.timestamp(message_datetime))
                e = discord.Embed(color=0xff5f39)
                e.title = "💸 Payment Successful 💸"
                from_sender_info = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (from_account_number,))
                to_receiver_info = await db.execute('SELECT * FROM accounts WHERE account_number = ?', (to_account_number,))
                sender_info = await from_sender_info.fetchone()
                receiver_info = await to_receiver_info.fetchone()
                sender_account_number = sender_info[0]
                receiver_account_number = receiver_info[0]
                sender_user_ign = sender_info[2]
                receiver_user_ign = receiver_info[2]
                e.add_field(
                    name="Sender",
                    value=f"📤 {sender_account_number}",
                    inline=False
                )
                e.add_field(
                    name="Receiver",
                    value=f"📥 {receiver_account_number}",
                    inline=False
                )
                e.add_field(
                    name="Amount",
                    value=f"💎 {formatted_amount}",
                    inline=False
                )
                e.add_field(
                    name="Timestamp",
                    value=f"⏰ <t:{timestamp}:f>",
                    inline=False
                )
                await ctx.send(embed=e, ephemeral=True)
                channel_id = 1164562229249712209
                channel = self.bot.get_channel(channel_id)
                if channel:
                    a = discord.Embed(color=0xff5f39)
                    a.title = "💸 Payment Successful 💸"
                    a.add_field(
                        name="Sender",
                        value=f"📤 {sender_account_number} | {sender_user_ign}",
                        inline=False
                    )
                    a.add_field(
                        name="Receiver",
                        value=f"📥 {receiver_account_number} | {receiver_user_ign}",
                        inline=False
                    )
                    a.add_field(
                        name="Amount",
                        value=f"💎 {formatted_amount}",
                        inline=False
                    )
                    a.add_field(
                        name="Timestamp",
                        value=f"⏰ <t:{timestamp}:f>",
                        inline=False
                    )
                    await channel.send(embed=a)
                else:
                    print(f"Channel with ID {channel_id} not found")
        except Exception as e:
            print(e)

    @commands.hybrid_command(description="List a Rosewood Casino Account's Balance")
    async def listbalance(self, ctx, account_number: int = None, user_id: str = None):
        if ctx.prefix == "!" and ctx.invoked_with in ["listbalance"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                async with aiosqlite.connect('dbs/balance.db') as db:
                    if account_number is not None:
                        cursor = await db.execute("SELECT * FROM accounts WHERE account_number = ?", (account_number,))
                    elif user_id is not None:
                        cursor = await db.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❌ Invalid Account Info ❌"
                        e.description = f"Enter a correct Account Number or User ID!"
                        await ctx.send(embed=e, ephemeral=True)
                        return
                    user_account = await cursor.fetchone()
                    if user_account:
                        formatted_balance = "${:,.2f}".format(user_account[1])
                        e = discord.Embed(color=0xff5f39)
                        e.title = "⚖️ Account Balance ⚖️"
                        e.add_field(
                            name="Account Number",
                            value=f"📋 {user_account[0]}",
                            inline=False
                        )
                        e.add_field(
                            name="Account Balance",
                            value=f"💰 {formatted_balance}",
                            inline=False
                        )
                        e.add_field(
                            name="User IGN",
                            value=f"📌 {user_account[2]}",
                            inline=False
                        )
                        await ctx.send(embed=e)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.title = "❓ Account Not Found ❓"
                        e.description = "No account found with the provided information."
                        await ctx.send(embed=e, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e, ephemeral=True)
    
    @commands.hybrid_command(description="Create a deposit log")
    async def depositlog(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["depositlog"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                def check_author(response):
                    return response.author == ctx.author
                async with aiosqlite.connect('dbs/deposit.db') as db:
                    await db.execute('''CREATE TABLE IF NOT EXISTS deposit_log (
                                        id INTEGER PRIMARY KEY,
                                        timestamp TEXT,
                                        log_number INTEGER,
                                        log_creator TEXT,
                                        account_number TEXT,
                                        guest_ign TEXT,
                                        guest_discord TEXT,
                                        deposit_amount TEXT,
                                        image TEXT
                                        )''')
                    cursor = await db.execute('SELECT MAX(log_number) FROM deposit_log')
                    last_log_number = await cursor.fetchone()
                    log_number = 1 if last_log_number[0] is None else last_log_number[0] + 1
                    await ctx.send("What is the Guest's Account number?")
                    account_response = await self.bot.wait_for("message", check=check_author)
                    account_number = account_response.content
                    await ctx.send("What is the Guest's IGN?")
                    ign_response = await self.bot.wait_for("message", check=check_author)
                    guest_ign = ign_response.content
                    await ctx.send("What is the Guest's Discord?")
                    discord_response = await self.bot.wait_for("message", check=check_author)
                    guest_discord = discord_response.content
                    await ctx.send("What is the deposit amount? [Only send the number, no commas]")
                    deposit_response = await self.bot.wait_for("message", check=check_author)
                    deposit_amount = deposit_response.content
                    await ctx.send("Send an image of the deposit!")
                    image_response = await self.bot.wait_for("message", check=check_author)
                    if image_response.attachments:
                        image_url = image_response.attachments[0].url
                    else:
                        await ctx.send("No image provided. Log creation cancelled.")
                        return
                    log_creator = ctx.author.name
                    message = ctx.message
                    message_datetime = message.created_at
                    timestamp = int(datetime.timestamp(message_datetime))
                    await db.execute('''INSERT INTO deposit_log (
                                        timestamp, log_number, log_creator, account_number, guest_ign, guest_discord, deposit_amount, image
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                        (timestamp, log_number, log_creator, account_number, guest_ign,
                                         guest_discord, deposit_amount, image_url))
                    await db.commit()
                    await ctx.send(f'**Deposit Log #{log_number}** created successfully')
                    log_channel = self.bot.get_channel(1163621118733733919)
                    deposit_amount = float(deposit_amount)
                    formatted_deposit = "${:,.2f}".format(deposit_amount)
                    if log_channel:
                        log_embed = discord.Embed(title=f"Deposit Log #{log_number}", color=0xff5f39)
                        log_embed.add_field(name="Log Creator", value=f"📄 {log_creator}", inline=False)
                        log_embed.add_field(name="Account Number", value=f"📋 {account_number}", inline=False)
                        log_embed.add_field(name="Guest IGN", value=f"📌 {guest_ign}", inline=False)
                        log_embed.add_field(name="Guest Discord", value=f"<:Discord:1143769008420692009> {guest_discord}", inline=False)
                        log_embed.add_field(name="Deposit Amount", value=f"💎 {formatted_deposit}", inline=False)
                        log_embed.add_field(name="Timestamp", value=f"⏰ <t:{timestamp}:f>", inline=False)
                        log_embed.set_image(url=image_url)
                        await log_channel.send(embed=log_embed)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)

    @commands.hybrid_command(description="Create a withdraw log")
    async def withdrawlog(self, ctx):
        if ctx.prefix == "!" and ctx.invoked_with in ["withdrawlog"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                def check_author(response):
                    return response.author == ctx.author
                async with aiosqlite.connect('dbs/withdraw.db') as db:
                    await db.execute('''CREATE TABLE IF NOT EXISTS withdraw_log (
                                        id INTEGER PRIMARY KEY,
                                        timestamp TEXT,
                                        log_number INTEGER,
                                        log_creator TEXT,
                                        account_number TEXT,
                                        guest_ign TEXT,
                                        guest_discord TEXT,
                                        withdraw_amount TEXT,
                                        image TEXT
                                        )''')
                    cursor = await db.execute('SELECT MAX(log_number) FROM withdraw_log')
                    last_log_number = await cursor.fetchone()
                    log_number = 1 if last_log_number[0] is None else last_log_number[0] + 1
                    await ctx.send("What is the Guest's Account number?")
                    account_response = await self.bot.wait_for("message", check=check_author)
                    account_number = account_response.content
                    await ctx.send("What is the Guest's IGN?")
                    ign_response = await self.bot.wait_for("message", check=check_author)
                    guest_ign = ign_response.content
                    await ctx.send("What is the Guest's Discord?")
                    discord_response = await self.bot.wait_for("message", check=check_author)
                    guest_discord = discord_response.content
                    await ctx.send("What is the withdraw amount? [Only send the number, no commas]")
                    withdraw_response = await self.bot.wait_for("message", check=check_author)
                    withdraw_amount = withdraw_response.content
                    await ctx.send("Send an image of the withdraw!")
                    image_response = await self.bot.wait_for("message", check=check_author)
                    if image_response.attachments:
                        image_url = image_response.attachments[0].url
                    else:
                        await ctx.send("No image provided. Log creation cancelled.")
                        return
                    log_creator = ctx.author.name
                    message = ctx.message
                    message_datetime = message.created_at
                    timestamp = int(datetime.timestamp(message_datetime))
                    await db.execute('''INSERT INTO withdraw_log (
                                        timestamp, log_number, log_creator, account_number, guest_ign, guest_discord, withdraw_amount, image
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                        (timestamp, log_number, log_creator, account_number, guest_ign,
                                         guest_discord, withdraw_amount, image_url))
                    await db.commit()
                    await ctx.send(f'**Withdraw Log #{log_number}** created successfully')
                    log_channel = self.bot.get_channel(1163621168046149672)
                    withdraw_amount = float(withdraw_amount)
                    formatted_withdraw = "${:,.2f}".format(withdraw_amount)
                    if log_channel:
                        log_embed = discord.Embed(title=f"Withdraw Log #{log_number}", color=0xff5f39)
                        log_embed.add_field(name="Log Creator", value=f"📄 {log_creator}", inline=False)
                        log_embed.add_field(name="Account Number", value=f"📋 {account_number}", inline=False)
                        log_embed.add_field(name="Guest IGN", value=f"📌 {guest_ign}", inline=False)
                        log_embed.add_field(name="Guest Discord", value=f"<:Discord:1143769008420692009> {guest_discord}", inline=False)
                        log_embed.add_field(name="Withdraw Amount", value=f"💎 {formatted_withdraw}", inline=False)
                        log_embed.set_image(url=image_url)
                        await log_channel.send(embed=log_embed)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)
    
    @commands.hybrid_command(description="List the user's with the highest Rosewood Account balance")
    async def baltop(self, ctx):
        async with aiosqlite.connect('dbs/balance.db') as db:
            cursor = await db.execute("SELECT user_ign, account_balance FROM accounts WHERE account_number NOT IN (1001, 1002) ORDER BY account_balance DESC LIMIT 10")
            rows = await cursor.fetchall()
        e = discord.Embed(color=0xff5f39)
        e.title="💮 Rosewood Casino Baltop 💮"
        for index, row in enumerate(rows, start=1):
            username, balance = row
            e.add_field(
                name=f"{index}) {username}", 
                value=f"💰 {balance:.2f}", 
                inline=False
            )
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(AccountCog(bot))