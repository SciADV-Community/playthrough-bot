#!python3
import discord, asyncio, sqlite3, config, modules.roles, re
from discord.ext import commands

class Channel():
    ### Fields ###
    def __init__(self, client):
        self.client = client
        print("Module {} loaded".format(self.__class__.__name__))

    ### Helper Functions ###
    # Get the channel ID of a certain user on the server where the command was on
    def owns(self, context):
        ret = None

        self.client.cursor.execute("SELECT ID, Game FROM Channel WHERE Owner = ? AND Guild = ?", (context.message.author.id, context.message.guild.id))
        channels = self.client.cursor.fetchall()
        if channels:
            ret = channels

        return ret
    
    # Retrieve certain information about the configuration of the current guild
    def fetch_guild_info(self, context, *fields):
        columns = ""
        for i in range(0, len(fields)):
            columns += fields[i]
            if i != len(fields) - 1:
                columns += ", "

        query="SELECT {} FROM Config WHERE Guild_ID = ?".format(columns)

        self.client.cursor.execute(query, (context.message.guild.id,))
        return self.client.cursor.fetchone()

    def fetch_game_guild_info(self, context, game, *fields):
        columns = ""
        for i in range(0, len(fields)):
            columns += fields[i]
            if i != len(fields) - 1:
                columns += ", "

        query="SELECT {0} FROM Game_Guild WHERE Guild_ID = ? AND Game_Name = ?".format(columns)

        self.client.cursor.execute(query, (context.message.guild.id, game,))
        return self.client.cursor.fetchone()


    # Allow/Block read permissions up to a certain chapter
    def set_chapter_perms(self, chapter, context, read):
        overwrite = dict()
        r = modules.roles.Roles(self.client)
        for i in range(1, chapter + 1):
            chapter_prefix = self.fetch_guild_info(context, 'Chapter_prefix')[0]
            target_role = r.find("{} {}".format(chapter_prefix, str(i)), context)
            if target_role is not None:
                overwrite[target_role] = discord.PermissionOverwrite(read_messages=read)
        return overwrite

    ### Commands ###
    # Creating a channel
    @commands.command(pass_context = True)
    async def start(self, context, game: str, name: str = None):
        if name is None: # if a name has not been given, give it a default value
            name = context.message.author.display_name

        # Handling for the default completion role
        self.client.cursor.execute("SELECT Name, Role_Name, Channel_suffix, Progress FROM Game JOIN Game_Alias ON Game.Name = Game_Alias.Game_Name WHERE Game.Name = ? OR Game_Alias.Alias = ?", (game, game.lower(),))
        game = self.client.cursor.fetchone()

        if not game:
            await context.send("No game specified or invalid game.")
            return
        else:
            has_channel = False
            channels = self.owns(context)
            if channels:
                for channel in channels:
                    if channel[1] == game[0]:
                        has_channel = True

            if has_channel:
                await context.send("You can only create 1 playthrough channel on this server for this game.")
                return

            role_name = game[1]
            channel_suffix = game[2]
            print(channel_suffix)
            main_game_role = modules.roles.Roles(self.client).find(role_name, context)
            if main_game_role is None:
                await context.send("The completion role {} for this game is not present in the server! Please let some administrator to create it. For this channel no permissions for those who have completed the game will be applied.".format(role_name))

        # Handling for the default category
        game_guild_info = self.fetch_game_guild_info(context, game[0], 'Start_category')
        if not game_guild_info:
            await context.send("No category to put the new channel in specified")
            return
        else:
            category = discord.utils.find(lambda c: c.id == game_guild_info[0], context.message.guild.categories)
        
        # Creating the channel
        # Setting the permissions
        overwrites = { # Basic permissions
            # Everyone
            context.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            # Creator
            context.message.author: discord.PermissionOverwrite(read_messages=True, manage_messages=True),
            # Bot
            context.message.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        if main_game_role is not None: # End-game permissions
            overwrites[main_game_role] = discord.PermissionOverwrite(read_messages=True)
            
        # default read chapter permissions
        if game[3] == 1:
        # chapter permission update based on user's roles
            guild_info = self.fetch_guild_info(context, 'Chapter_prefix', 'Main_Game')
            if game[0] == guild_info[1]:
                overwrites.update(self.set_chapter_perms(12, context, True))
                for role in context.message.author.roles:
                    if re.match("{} \d+".format(guild_info[0]), role.name):
                        overwrites.update(self.set_chapter_perms(int(re.search('\d+', role.name).group()), context, False))
                        break
        
        # Creating the channel and setting the category
        channel = await context.message.guild.create_text_channel('{}-plays-{}'.format(name, channel_suffix), overwrites=overwrites, reason="New playthrough channel!")
        if category is not None:
            await channel.edit(category=category)

        # Saving to the database
        self.client.cursor.execute("INSERT INTO Channel (ID, Owner, Guild, Game) VALUES (?, ?, ?, ?)", (channel.id, context.message.author.id, context.message.guild.id, game[0]))
        self.client.database.commit()

        await context.send("Successfully created your playthrough channel! Have fun!")

    # Archiving a channel
    @commands.command(pass_context=True)
    async def end(self, context):
        self.client.cursor.execute("SELECT Owner, Game FROM Channel WHERE ID = ?", (context.message.channel.id,))
        chan = self.client.cursor.fetchone()
        if not chan:
            await context.send("You don't have permissions to move this channel.")
        if int(chan[0]) == context.message.author.id:
            channel = discord.utils.find(lambda c: c.id == context.message.channel.id, context.message.guild.text_channels)
            if channel is not None:
                archive_category = discord.utils.find(lambda c: c.id == self.fetch_game_guild_info(context, chan[1], 'Archive_category')[0], context.message.guild.categories)
                if archive_category:
                    await channel.edit(category=archive_category)
                    await context.send("Archived your playthrough channel. Hope you had fun!")
                else:
                    await context.send("No archive category set. Channel not archived. Let an administrator know that they should add an archiving category using the command `{}admin set Archive_category`".format(config.mod))
            else:
                await context.send("You have not even started a playthrough yet! `{}end` is not if you have finished the game, use `{}finished` instead!.".format(config.mod, config.mod))
        else:
            await context.send("You don't have permissions to move this channel.")
        

def setup(client):
    client.add_cog(Channel(client))
        