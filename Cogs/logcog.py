import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite

# Logging Events Class
class LogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.create_table()
    
    async def create_table(self):
        self.db_conn = await aiosqlite.connect("dbs/logging.db")
        await self.db_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logging_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
            """
        )
        await self.db_conn.commit()
    
    async def get_logging_channel(self, guild_id):
        async with self.db_conn.execute(
            "SELECT channel_id FROM logging_channels WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None
    
    @commands.hybrid_command(description="Set the servers logging channel")
    async def setlog(self, ctx, channel: discord.TextChannel):
        if ctx.prefix == "!" and ctx.invoked_with in ["setlog"]:
            return
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            await self.db_conn.execute(
                "INSERT OR REPLACE INTO logging_channels (guild_id, channel_id) VALUES (?, ?)",
                (ctx.guild.id, channel.id),
            )
            await self.db_conn.commit()
            confirm_message = await ctx.send(f"Is {channel.mention} the correct channel? [Yes/No]")
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                response = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await confirm_message.delete()
                await ctx.send("Timed out. Logging channel setting cancelled.")
                return
            if response.content.lower() == "yes":
                await ctx.send(f"Confirmed! Logging channel set to {channel.mention}!")
            else:
                await self.db_conn.execute(
                    "DELETE FROM logging_channels WHERE guild_id = ?", (ctx.guild.id,)
                )
                await self.db_conn.commit()
                await ctx.send("Logging channel setting cancelled.")
            await confirm_message.delete()
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        logging_channel = await self.get_logging_channel(message.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="🗑️ Message Deleted")
            e.set_thumbnail(url=f"{message.author.avatar.url}")
            if message.content:
                e.description = f"A message by {message.author.mention} was deleted \n<:Reply:1123773242327441468> In <#{message.channel.id}> \n \n> {message.content}"
            elif message.attachments:
                e.description = f"A message by {message.author.mention} was deleted \n<:Reply:1123773242327441468> In <#{message.channel.id}>"
                attachment_url = message.attachments[0].url
                e.set_image(url=attachment_url)
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        logging_channel = await self.get_logging_channel(before.guild.id)
        if logging_channel:
            if before.author.bot:
                return
            else:
                channel = self.bot.get_channel(logging_channel)
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="📝 Message Edited")
                e.set_thumbnail(url=f"{before.author.avatar.url}")
                e.description = f"{before.author.mention} edited their message \n<:Reply:1123773242327441468> In <#{before.channel.id}>" 
                e.add_field(name="__Before__", value=f"> {before.content}")
                e.add_field(name="__After__", value=f"> {after.content}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging_channel = await self.get_logging_channel(member.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="📈 Member Joined")
            e.set_thumbnail(url=f"{member.avatar.url}")
            e.add_field(name="__Member__", value=f"> {member.mention}")
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logging_channel = await self.get_logging_channel(member.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="📉 Member Left")
            e.set_thumbnail(url=f"{member.avatar.url}")
            e.add_field(name="__Member__", value=f"> {member.mention}")
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        logging_channel = await self.get_logging_channel(member.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            logs = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
            logs = logs[0]
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="🚨 Member Banned")
            e.set_thumbnail(url=f"{member.avatar.url}")
            e.add_field(name="__Member__", value=f"> {member.mention}")
            e.add_field(name="__Ban Reason__", value=f"> {logs.reason}", inline=False)
            e.add_field(name="__Staff Member__", value=f"> {logs.user.mention}", inline=False)
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        logging_channel = await self.get_logging_channel(member.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="✨ Member Unbanned")
            e.set_thumbnail(url=f"{member.avatar.url}")
            e.add_field(name="__Member__", value=f"> {member.mention}")
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        logging_channel = await self.get_logging_channel(before.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            if len(before.roles) > len(after.roles):
                droles = next(droles for droles in before.roles if droles not in after.roles)
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🧮 Role Update")
                e.set_thumbnail(url=f"{before.avatar.url}")
                e.add_field(name="__Member__", value=f"> {before.mention}")
                e.add_field(name="__Role__", value=f"> ❌ {droles}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)
            else:
                if len(before.roles) < len(after.roles):
                    aroles = next(aroles for aroles in after.roles if aroles not in before.roles)
                    e = discord.Embed(color=0xff5f39)
                    e.set_author(name="🧮 Role Update")
                    e.set_thumbnail(url=f"{before.avatar.url}")
                    e.add_field(name="__Member__", value=f"> {before.mention}")
                    e.add_field(name="__Role__", value=f"> ✅ {aroles}", inline=False)
                    e.timestamp = datetime.utcnow()
                    await channel.send(embed=e)          
            if before.display_name != after.display_name:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🧾 Nickname Update")
                e.set_thumbnail(url=f"{before.avatar.url}")
                e.add_field(name="__Member__", value=f"> {before.mention}")
                e.add_field(name="__Before__", value=f"> {before.display_name}", inline=False)
                e.add_field(name="__After__", value=f"> {after.display_name}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)
        
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        logging_channel = await self.get_logging_channel(before.guild.id)
        channel = self.bot.get_channel(logging_channel)
        if logging_channel:
            if before.name != after.name:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🧾 Account Name Update")
                e.set_thumbnail(url=f"{before.avatar.url}")
                e.add_field(name="__Member__", value=f"> {before.mention}")
                e.add_field(name="__Before__", value=f"> {before.name}#{before.discriminator}", inline=False)
                e.add_field(name="__After__", value=f"> {after.name}#{after.discriminator}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        logging_channel = await self.get_logging_channel(channel.guild.id)
        if logging_channel:
            chan = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="📥 Channel Created")
            e.add_field(name="__Name__", value=f"> {channel.name}")
            e.add_field(name="__Mention__", value=f"> {channel.mention}", inline=False)
            e.add_field(name="__Channel ID__", value=f"> {channel.id}", inline=False)
            e.timestamp = datetime.utcnow()
            await chan.send(embed=e)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logging_channel = await self.get_logging_channel(channel.guild.id)
        if logging_channel:
            chan = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="📤 Channel Deleted")
            e.add_field(name="__Name__", value=f"> {channel.name}")
            e.add_field(name="__Mention__", value=f"> {channel.mention}", inline=False)
            e.add_field(name="__Channel ID__", value=f"> {channel.id}", inline=False)
            e.timestamp = datetime.utcnow()
            await chan.send(embed=e)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        logging_channel = await self.get_logging_channel(member.guild.id)
        chan = self.bot.get_channel(logging_channel)
        if logging_channel:
            if before.channel and after.channel and before.channel != after.channel:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🔊 Moved VC's")
                e.add_field(name="__User__", value=f"> {member.mention}")
                e.add_field(name="__Moved From__", value=f"> {before.channel.name}", inline=False)
                e.add_field(name="__Moved To__", value=f"> {after.channel.name}", inline=False)
                e.timestamp = datetime.utcnow()
                await chan.send(embed=e)
            elif before.channel and not after.channel:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🔊 Left VC")
                e.add_field(name="__User__", value=f"> {member.mention}")
                e.add_field(name="__Left__", value=f"> {before.channel.name}", inline=False)
                e.timestamp = datetime.utcnow()
                await chan.send(embed=e)
            elif not before.channel and after.channel:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🔊 Joined VC")
                e.add_field(name="__User__", value=f"> {member.mention}")
                e.add_field(name="__Joined__", value=f"> {after.channel.name}", inline=False)
                e.timestamp = datetime.utcnow()
                await chan.send(embed=e)
            
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        logging_channel = await self.get_logging_channel(channel.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="🎭 Role Created")
            e.add_field(name="__Role Mention__", value=f"> {role.mention}")
            e.add_field(name="__Role Name__", value=f"> {role.name}", inline=False)
            e.add_field(name="__Role ID__", value=f"> {role.id}", inline=False)
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        logging_channel = await self.get_logging_channel(role.guild.id)
        if logging_channel:
            channel = self.bot.get_channel(logging_channel)
            e = discord.Embed(color=0xff5f39)
            e.set_author(name="🎭 Role Deleted")
            e.add_field(name="__Role Mention__", value=f"> {role.mention}")
            e.add_field(name="__Role Name__", value=f"> {role.name}", inline=False)
            e.add_field(name="__Role ID__", value=f"> {role.id}", inline=False)
            e.timestamp = datetime.utcnow()
            await channel.send(embed=e)
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        logging_channel = await self.get_logging_channel(before.guild.id)
        channel = self.bot.get_channel(logging_channel)
        if logging_channel:
            if before.name != after.name:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🎭 Role Update")
                e.add_field(name="__Before__", value=f"> {before.name}")
                e.add_field(name="__After__", value=f"> {after.name}", inline=False)
                e.add_field(name="__Role ID__", value=f"> {after.id}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)
            if before.color != after.color:
                e = discord.Embed(color=0xff5f39)
                e.set_author(name="🎭 Role Update")
                e.add_field(name="__Before__", value=f"> {before.color}")
                e.add_field(name="__After__", value=f"> {after.color}", inline=False)
                e.add_field(name="__Role ID__", value=f"> {after.id}", inline=False)
                e.timestamp = datetime.utcnow()
                await channel.send(embed=e)
    

async def setup(bot):
    await bot.add_cog(LogCog(bot))