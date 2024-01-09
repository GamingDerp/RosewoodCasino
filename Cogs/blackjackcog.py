import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import aiosqlite
import random
import asyncio
import traceback

card_emojis = {
    "2 of Clubs": "<:two_of_clubs:1164905011499774083>",
    "3 of Clubs": "<:three_of_clubs:1164904962879406080>",
    "4 of Clubs": "<:four_of_clubs:1164879953725243452>",
    "5 of Clubs": "<:five_of_clubs:1164879926688751626>",
    "6 of Clubs": "<:six_of_clubs:1164904868566278244>",
    "7 of Clubs": "<:seven_of_clubs:1164904817169272893>",
    "8 of Clubs": "<:eight_of_clubs:1164879887534923806>",
    "9 of Clubs": "<:nine_of_clubs:1164904697509982238>",
    "10 of Clubs": "<:ten_of_clubs:1164904915592810526>",
    "Jack of Clubs": "<:jack_of_clubs:1164879961811861504>",
    "Queen of Clubs": "<:queen_of_clubs:1164904761707999302>",
    "King of Clubs": "<:king_of_clubs:1164879991109058610>",
    "Ace of Clubs": "<:ace_of_clubs:1164879839887626311>",
    "2 of Diamonds": "<:two_of_diamonds:1164905022404956292>",
    "3 of Diamonds": "<:three_of_diamonds:1164904975793672302>",
    "4 of Diamonds": "<:four_of_diamonds:1164879955923050576>",
    "5 of Diamonds": "<:five_of_diamonds:1164879928802685058>",
    "6 of Diamonds": "<:six_of_diamonds:1164904880364851240>",
    "7 of Diamonds": "<:seven_of_diamonds:1164904830326804530>",
    "8 of Diamonds": "<:eight_of_diamonds:1164879899266392124>",
    "9 of Diamonds": "<:nine_of_diamonds:1164904715591630868>",
    "10 of Diamonds": "<:ten_of_diamonds:1164904927466881154>",
    "Jack of Diamonds": "<:jack_of_diamonds:1164879964454260776>",
    "Queen of Diamonds": "<:queen_of_diamonds:1164904774479642665>",
    "King of Diamonds": "<:king_of_diamonds:1164879995244662874>",
    "Ace of Diamonds": "<:ace_of_diamonds:1164879855016497162>",
    "2 of Hearts": "<:two_of_hearts:1164876013927415868>",
    "3 of Hearts": "<:three_of_hearts:1164904988452061324>",
    "4 of Hearts": "<:four_of_hearts:1164879957453979669>",
    "5 of Hearts": "<:five_of_hearts:1164879931499618424>",
    "6 of Hearts": "<:six_of_hearts:1164904892935192606>",
    "7 of Hearts": "<:seven_of_hearts:1164904843756970014>",
    "8 of Hearts": "<:eight_of_hearts:1164879921143894106>",
    "9 of Hearts": "<:nine_of_hearts:1164904734944133261>",
    "10 of Hearts": "<:ten_of_hearts:1164904939294838884>",
    "Jack of Hearts": "<:jack_of_hearts:1164879984695975936>",
    "Queen of Hearts": "<:queen_of_hearts:1164904788836757504>",
    "King of Hearts": "<:king_of_hearts:1164880000617545819>",
    "Ace of Hearts": "<:ace_of_hearts:1164879865116377138>",
    "2 of Spades": "<:two_of_spades:1164876011654090822>",
    "3 of Spades": "<:three_of_spades:1164905001504735302>",
    "4 of Spades": "<:four_of_spades:1164879958733230140>",
    "5 of Spades": "<:five_of_spades:1164879934389493781>",
    "6 of Spades": "<:six_of_spades:1164904905518108792>",
    "7 of Spades": "<:seven_of_spades:1164904856922882068>",
    "8 of Spades": "<:eight_of_spades:1164879924381880360>",
    "9 of Spades": "<:nine_of_spades:1164904746918887434>",
    "10 of Spades": "<:ten_of_spades:1164904949994487889>",
    "Jack of Spades": "<:jack_of_spades:1164879988164661258>",
    "Queen of Spades": "<:queen_of_spades:1164904804489895967>",
    "King of Spades": "<:king_of_spades:1164880004090433558>",
    "Ace of Spades": "<:ace_of_spades:1164879877464395786>",
}

class BlackJackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_state = {}

    @commands.hybrid_command(description="Play a game of Blackjack")
    async def blackjack(self, ctx, bet: int):
        if ctx.prefix == "!" and ctx.invoked_with in ["blackjack"]:
            return
        bjchannel = 1169444380617232497
        bdchannel = 1163616023073783938
        min_bet = 25
        max_bet = 25000
        if ctx.channel.id == bjchannel or ctx.channel.id == bdchannel:
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
                    e.description = "The minimum bet for **Blackjack** is **$25**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if bet > max_bet:
                    e.title = "💰 Maximum Bet 💰"
                    e.description = "The maximum bet for **Blackjack** is **$25,000**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                if bet > account_balance:
                    formatted_bet = "${:,.2f}".format(bet)
                    e.title = "⛔️ Insufficient Balance ⛔️"
                    e.description = f"You are unable to bet **{formatted_bet}**!"
                    await ctx.send(embed=e, ephemeral=True)
                    return
                player_hand = [self.draw_card() for _ in range(2)]
                dealer_hand = [self.draw_card() for _ in range(2)]
                player_score = self.calculate_score(player_hand)
                dealer_score = self.calculate_dealer_score(dealer_hand)
                if player_score == 21:
                    await self.end_game(ctx)
                if dealer_score == 21:
                    await self.end_game(ctx)
                    return
                else:
                    user_id = ctx.author.id
                    async with aiosqlite.connect('dbs/balance.db') as db:
                        await db.execute('UPDATE accounts SET account_balance = account_balance - ? WHERE user_id = ?', (bet, user_id))
                        await db.commit()
                    e = discord.Embed(color=0xff5f39)
                    e.title = "♣️ Blackjack ♣️"
                    player_hand_emojis = [card_emojis[card] for card in player_hand]
                    dealer_hand_emojis = [card_emojis[card] for card in dealer_hand]
                    player_hand_message = " ".join(player_hand_emojis)
                    dealer_hand_message = " ".join(dealer_hand_emojis)
                    e.add_field(name="Your Hand", value=f"{player_hand_message} ({player_score})", inline=False)
                    e.add_field(name="Dealer's Hand", value=f"{dealer_hand_message} ({dealer_score})", inline=False)
                    view = discord.ui.View()
                    hit_button = discord.ui.Button(style=discord.ButtonStyle.success, label="🃏 Hit", custom_id="hit")
                    stand_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="🛑 Stand", custom_id="stand")
                    view.add_item(hit_button)
                    view.add_item(stand_button)
                    message = await ctx.send(embed=e, view=view)
                    self.game_state[message.id] = {
                        "player_id": user_id,
                        "player_hand": player_hand,
                        "dealer_hand": dealer_hand,
                        "player_score": player_score,
                        "dealer_score": dealer_score,
                        "bet": bet,
                    }
            except Exception as e:
                print(e)
        else:
            e = discord.Embed(color=0xff5f39)
            e.title = "❌ Incorrect Channel ❌"
            e.description = "This isn't the correct channel! Head to <#1169444380617232497> to use **Blackjack**!"
            await ctx.send(embed=e, ephemeral=True)
            return

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            if interaction.type != discord.InteractionType.component:
                return
            game_data = self.game_state.get(interaction.message.id)
            if game_data is None:
                return
            if interaction.user and interaction.user.id != game_data.get("player_id"):
                response_embed = discord.Embed(
                    color=0xff5f39,
                    title="❌ Not Your Game! ❌",
                    description="This is not your game of **Blackjack**! Go away!",
                )
                await interaction.response.send_message(embed=response_embed, ephemeral=True)
                return
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'hit':
                    await self.hit_logic(interaction, game_data)
            if interaction.type == discord.InteractionType.component:
                if interaction.data['custom_id'] == 'stand':
                    await self.stand_logic(interaction, game_data)
                    await self.end_game(interaction, game_data)
        except Exception as e:
            print(e)

    async def hit_logic(self, interaction, game_data):
        new_card = self.draw_card()
        game_data["player_hand"].append(new_card)
        game_data["player_score"] = self.calculate_score(game_data["player_hand"])
        player_hand_message = " ".join([card_emojis[card] for card in game_data["player_hand"]])
        dealer_hand_message = " ".join([card_emojis[card] for card in game_data["dealer_hand"]])
        new_embed = discord.Embed(color=0xff5f39)
        new_embed.title = "♣️ Blackjack ♣️"
        new_embed.add_field(name="Your Hand", value=f"{player_hand_message} ({game_data['player_score']})", inline=False)
        new_embed.add_field(name="Dealer's Hand", value=f"{dealer_hand_message} ({game_data['dealer_score']})", inline=False)
        if game_data["player_score"] == 21:
            await self.end_game(interaction, game_data)
        elif game_data["player_score"] > 21:
            await self.end_game(interaction, game_data)
        else:
            await interaction.response.edit_message(embed=new_embed)

    async def stand_logic(self, interaction, game_data):
        dealer_hand = game_data["dealer_hand"]
        player_score = game_data['player_score']
        dealer_score = self.calculate_dealer_score(dealer_hand)
        win_probability = 0
        if dealer_score <= 11:
            win_probability = 0.4
        elif dealer_score < player_score:
            win_probability = 0.2
        elif dealer_score == 18:
            win_probability = 0.04
        elif dealer_score == 19:
            win_probability = 0.02
        elif dealer_score == 20:
            win_probability = 0.001
        if random.random() < win_probability:
            new_card = self.draw_card()
            dealer_hand.append(new_card)
            dealer_score = self.calculate_dealer_score(dealer_hand)
        dealer_hand_message = " ".join([card_emojis[card] for card in dealer_hand])
        new_embed = interaction.message.embeds[0]
        new_embed.set_field_at(1, name="Dealer's Hand", value=f"{dealer_hand_message} ({dealer_score})", inline=False)
        if player_score == 21 or player_score > 21:
            await self.end_game(interaction, game_data)
        else:
            await self.end_game(interaction, game_data)

    async def end_game(self, interaction, game_data):
        message_id = interaction.message.id
        if not self.game_state:
            return
        dealer_hand = self.game_state[message_id]["dealer_hand"]
        dealer_score = self.calculate_score(dealer_hand)
        while dealer_score < 17:
            new_card = self.draw_card()
            dealer_hand.append(new_card)
            dealer_score = self.calculate_score(dealer_hand)
        player_hand = game_data["player_hand"]
        player_score = game_data["player_score"]
        bet = game_data["bet"]
        winnings = 0
        result_message = ""
        if player_score > 21 and dealer_score > 21:
            result_message = "Both players lost!"
        elif player_score > 21:
            result_message = "Dealer wins!"
        elif dealer_score > 21:
            winnings = 2 * bet
            formatted_winnings = "$**{:,.2f}**".format(winnings)
            result_message = f"You win {formatted_winnings}! 🎉"
        elif dealer_score > player_score:
            result_message = "Dealer wins!"
        elif dealer_score < player_score:
            winnings = 2 * bet
            formatted_winnings = "$**{:,.2f}**".format(winnings)
            result_message = f"You win {formatted_winnings}! 🎉"
        else:
            winnings = bet
            formatted_winnings = "$**{:,.2f}**".format(winnings)
            result_message = "It's a tie!"
        dealer_hand_message = " ".join([card_emojis[card] for card in dealer_hand])
        player_hand_message = " ".join([card_emojis[card] for card in player_hand])
        user_id = game_data["player_id"]
        async with aiosqlite.connect('dbs/balance.db') as db:
            await db.execute('UPDATE accounts SET account_balance = account_balance + ? WHERE user_id = ?', (winnings, user_id))
            await db.commit()
        new_embed = discord.Embed(color=0xff5f39)
        new_embed.title = "♣️ Blackjack ♣️"
        new_embed.add_field(name="Your Hand", value=f"{player_hand_message} ({player_score})", inline=False)
        new_embed.add_field(name="Dealer's Hand", value=f"{dealer_hand_message} ({dealer_score})", inline=False)
        new_embed.description = result_message
        await interaction.response.edit_message(embed=new_embed, view=None)
        del self.game_state[message_id]

    def draw_card(self):
        return random.choice(list(card_emojis.keys()))

    def calculate_score(self, hand):
        score = 0
        num_aces = 0
        for card in hand:
            card_rank = card.split(" ")[0]
            if card_rank.isdigit():
                score += int(card_rank)
            elif card_rank in ("Jack", "Queen", "King"):
                score += 10
            elif card_rank == "Ace":
                score += 11
                num_aces += 1
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
        return score
    
    def calculate_dealer_score(self, hand):
        score = 0
        num_aces = 0
        for card in hand:
            card_rank = card.split(" ")[0]
            if card_rank.isdigit():
                score += int(card_rank)
            elif card_rank in ("Jack", "Queen", "King"):
                score += 10
            elif card_rank == "Ace":
                score += 11
                num_aces += 1
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
        return score


async def setup(bot):
    await bot.add_cog(BlackJackCog(bot))