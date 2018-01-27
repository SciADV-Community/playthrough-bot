# playthrough-bot
A Discord bot made using [Discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) (rewrite) to handle channels / roles / games for multiple discord playthrough servers.

## What is a playthrough server?
Some people like discussing the events of a certain visual novel or video game as they go throguh it and "blog" somewhere about their current thoughts on said game or VN. Especially in the case of VNs where there are multiple plot twists constantly, having fairly general spoiler channels in discord servers dedicated to said VN for discussion of the game is not really feasible, as people visiting those as they play are very prone to getting spoiled themselves.
And that's the purpose of playthrough servers. In such servers there are multiple channels, each dedicated to one user, where that user can blog about their playthrough without any worry of spoiling or getting spoiled. Users who are at the same point or ahead of the current user in the game can also view those channels and discuss about certain topics.

## What does this bot do to aid playthroguh servers?
This bot offers functionality to add a role for a certain chapter in the game to a certain user, or a role that signals that the user has completed the game. This is how channel visibility is handled. It also gives the users the ability to create their own channels, and manages the permissions for those channels as those users progress through the game.

## What it does not do?
Set up the other non-personal channels and roles for the chapters / game completion. The administrators of the server must add those themselves.

# Installation
The installation of this bot is very simple, one needs to:
* Download the latest python 3 version.
* Install the latest version of the Discord.py rewrite branch (see installation instructions on the discord.py github linked at the top)
* Edit sample_config.py to have a valid bot token and valid bot master ID
* Rename sample_config.py to config.py
* Run bot.py
