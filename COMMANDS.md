# 📋 Command List
This is a list of all commands, a description, and their usage.

All commands are slash commands. [Except commands in `main.py` and *some* staff commands]

## 📌 General
Command | Description | Usage
--- | --- | ---
help | Help menu displaying public commands | `help`
info | Shows information about the bot | `info`
test | Tests if the bot is up | `test`
ping | Shows a users ping | `ping`
suggest | Posts a users suggestion in the suggestion channel | `suggest <suggestion>`
feecalc | Calculates the fee of a withdraw | `feecalc <amount>`

## 🎳 Games
Command | Description | Usage
--- | --- | ---
coinflip | Flips a coin, Heads = Win | `coinflip <bet>`
duelflip | Challenges another user to a coinflip duel | `duelflip <user> <bet>`
slots | Plays a game of slots | `slots <bet>`
crash | Starts a game of crash | `crash`
buy | Buys into an ongoing crash game | `buy <bet>`
out | Gets out of an ongoing crash game | `out`
blackjack | Starts a game of blackjack | `blackjack <bet>`
roulette | Plays a game of roulette [Can only choose one option at a time] | `roulette <bet> <color> <number> <odds>`
sixes | Plays a game of sixes | `sixes`
bet | Buys into a side of an ongoing bet | `buy <side_name> <bet>`

## 📰 Account
Command | Description | Usage
--- | --- | ---
createaccount | Creates a casino account | `createaccount <user_ign>`
deleteaccount | Deletes a users casino account | `deleteaccount`
balance | Shows a users balance | `balance`
pay | Pays another user | `pay <from_account_number> <to_account_number> <amount>`
baltop | Shows the top ten users with the highest balance | `baltop`

## ⚙️ Staff
Command | Description | Usage
--- | --- | ---
postverify | Posts the verification embed | `!postverify`
selfroles | Posts the selfroles embed | `!selfroles`
setsuggest | Sets the suggestion channel | `setsuggest`
setlog | Sets the logging channel | `setlog <channel>`
posttutorial | Posts the tutorial embed | `!posttutorial`
giveaway | Creates a giveaway | `giveaway <time> <time> <winners> <prize>`
createbet | Creates a bet [Minimum of 2 sides needed] | `createbet <time_limit> <side1> <side1_odds> <side2> <side2_odds> <etc> <etc>` 
winner | Sets the winning side of the bet | `winner <side_name>`
forcedelete | Forcefully deletes a users casino account | `forcedelete <account_number>`
editnumber | Edits a casino accounts number | `editnumber <current_account_number> <new_account_number>`
editign | Edits a casino accounts ign | `editign <account_number> <new_ign>`
deposit | Deposits money into a casino account | `deposit <account_number> <amount>`
withdraw | Withdraws money from a casino account | `withdraw <account_number> <amount>`
listbalance | Lists the balance of a casino account [Only use one option at a time] | `listbalance <account_number> <user_id>`
depositlog | Creates a "deposit log" [Be sure to read the questions, be prepared] | `depositlog`
withdrawlog | Creates a "withdraw log" [Be sure to read the questions, be prepared] | `withdrawlog`
poll | Creates a poll [Up to 5 options] | `poll <question> <option1> <option2> <etc>`
reload | Reloads a cog | `!reload <cog_name>`
loadcog | Loads a cog | `!loadcog <cog_name>`
unloadcog | Unloads a cog | `!unloadcog <cog_name>`
sync | Syncs commands to the bot tree | `!sync`
