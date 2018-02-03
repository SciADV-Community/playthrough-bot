#!python3
import discord, asyncio, sqlite3, config, modules.admin
from discord.ext import commands

class Game:
    ### Fields ###
    def __init__(self, client):
        self.client = client
        print("Module {} loaded".format(self.__class__.__name__))

    ### Helper Functions ###
    # Fetch the Name of a Game
    def fetch_game(self, game):
        ret = None

        self.client.cursor.execute("SELECT * FROM Game WHERE Name = ?", (game,))
        game_result = self.client.cursor.fetchone()
        if game_result:
            ret = game_result

        return ret

    # Add aliases
    def addalias(self, client, game, alias):
        self.client.cursor.execute("INSERT INTO Game_Alias (Alias, Game_Name) VALUES (?, ?)", (alias, game,))
    
    ### Commands ###
    # Get info about a game 
    @commands.command(pass_context=True)
    async def gameinfo(self, context, game: str):
        game_result = self.fetch_game(game)
        if game_result is not None: # If a game has been found
            # get aliases
            self.client.cursor.execute("SELECT Alias FROM Game_Alias WHERE Game_Name = ?", (game,))
            alias_result = self.client.cursor.fetchall()
            # Make embed
            embed = discord.Embed(title=game_result[0], colour = 0x42c6ff)
            embed.add_field(name="Role: ", value=game_result[1], inline=True)
            aliases = ""
            for alias in alias_result:
                aliases += alias[0] + " "
            embed.add_field(name="Aliases: ", value=aliases)
            # send embed
            await context.send(embed=embed)
        else: # not found
            await context.send("{} not found.".format(game))

    # add a game
    @commands.command(pass_context=True)
    async def addgame(self, context, game: str, role: str, progress: str, channel_suffix: str, *aliases):
        if self.fetch_game(game) is not None: # if it exists
            await context.send("Game {} already exists".format(game))
        else: # if not
            if modules.admin.Admin(self.client).is_admin(context):
                # Parsing the progress parameter
                if progress == "Yes":
                    prog = 1
                else:
                    prog = 0
                # insert the game info
                self.client.cursor.execute("INSERT INTO Game (Name, Role_Name, Progress, Channel_suffix) VALUES (?, ?, ?, ?)", (game, role, prog, channel_suffix,))
                # insert all the aliases
                if aliases is not None:
                    for alias in aliases:
                        self.addalias(self.client, game, alias)
                self.client.database.commit()
                await context.send("Game {} added.".format(game))
            else:
                await context.send("You do not have the required permissions for this (manage roles).")

    # add an alias to a game
    @commands.command(pass_context=True)
    async def addaliases(self, context, game: str, *aliases):
        if self.fetch_game(game): # if it exists
            if modules.admin.Admin(self.client).is_admin(context):
                for alias in aliases:
                    self.addalias(self.client, game, alias)
                self.client.database.commit()
            else:
                await context.send("You do not have the required permissions for this (manage roles).")
        else:
            await context.send("{} not found.".format(game))


def setup(client):
    client.add_cog(Game(client))