import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import random
import asyncio

class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.participants = {}
    
    def has_joined(self, user, giveaway_id):
        return user.id in self.participants.get(giveaway_id, [])

    @commands.hybrid_command(description="Start a giveaway")
    async def giveaway(self, ctx, time, winners, *, prize: str):
        if discord.utils.get(ctx.author.roles, name="Casino Owner"):
            try:
                winners = int(winners)
                converted_duration = self.convert_duration(time)
                if converted_duration == -1:
                    return
                end_time = datetime.utcnow() + converted_duration
                e = discord.Embed(
                    title="🎉 Giveaway 🎉",
                    color=0xff5f39
                )
                e.add_field(
                    name="Time",
                    value=f"⏰ {time}",
                    inline=False
                )
                e.add_field(
                    name="Winners",
                    value=f"👑 {winners}",
                    inline=False
                )
                e.add_field(
                    name="Prize",
                    value=f"🎁 {prize}",
                    inline=False
                )
                e.add_field(
                    name="Entries",
                    value=f"📬 0",
                    inline=False
                )
                view = discord.ui.View()
                join_button = discord.ui.Button(style=discord.ButtonStyle.success, label="📮 Join", custom_id="join")
                view.add_item(join_button)
                message = await ctx.send("<@&1173401429671673937>", embed=e, view=view)
                await asyncio.sleep(converted_duration.total_seconds())
                winners_list = random.sample(self.participants.get(message.id, []), winners)
                winners_text = "\n".join([f"**👑 Winner(s):** <@{winner}>" for i, winner in enumerate(winners_list)])
                winners_embed = discord.Embed(
                    title="🎉 Giveaway Results 🎉",
                    description=f"**🎁 Prize:** {prize}\n{winners_text}",
                    color=0xff5f39
                )
                await ctx.send(embed=winners_embed)
                view.clear_items()
                await message.edit(view=view)
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.description = "🚨 That is a **Casino Owner** command! You don't have the required perms! 🚨"
            await ctx.send(embed=e)
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'join':
                    if discord.utils.get(interaction.user.roles, name="Account Holder"):
                        user = interaction.user
                        giveaway_id = interaction.message.id
                        if giveaway_id not in self.participants:
                            self.participants[giveaway_id] = []
                        if not self.has_joined(user, giveaway_id):
                            self.participants[giveaway_id].append(user.id)
                            entries = len(self.participants.get(giveaway_id, []))
                            e = interaction.message.embeds[0]
                            e.set_field_at(3, name="Entries", value=f"📬 {entries}", inline=False)
                            await interaction.message.edit(embed=e)
                            e = discord.Embed(color=0xff5f39)
                            e.title = f"🎉 Giveaway Joined! 🎉"
                            e.description = f"You joined the giveaway!"
                            await interaction.response.send_message(embed=e, ephemeral=True)
                        else:
                            self.participants[giveaway_id].remove(user.id)
                            entries = len(self.participants.get(giveaway_id, []))
                            e = interaction.message.embeds[0]
                            e.set_field_at(3, name="Entries", value=f"📬 {entries}", inline=False)
                            await interaction.message.edit(embed=e)
                            e = discord.Embed(color=0xff5f39)
                            e.title = f"🎉 Giveaway Left! 🎉"
                            e.description = f"You left the giveaway!"
                            await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        e = discord.Embed(color=0xff5f39)
                        e.description = "🚨 That is a **Account Holder** action! Head to <#1163647875423674471> to create an account! 🚨"
                        await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as e:
            print(e)

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
    await bot.add_cog(GiveawayCog(bot))