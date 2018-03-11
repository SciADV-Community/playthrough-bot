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

        self.client.cursor.execute("SELECT ID FROM Channel WHERE Owner = ? AND Guild = ?", (context.message.author.id, context.message.guild.id))
        channel = self.client.cursor.fetchone()
        if channel:
            ret = channel[0]

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
    async def start(self, context, name: str = None):
        if self.owns(context) is not None: # if a user already has a channel
            await context.send("You can only create 1 playthrough channel on this server.")
        else:
            if name is None: # if a name has not been given, give it a default value
                name = context.message.author.display_name

            # Fetching basic info from the guild
            guild_info = self.fetch_guild_info(context, 'Start_category', 'Main_game', 'Chapter_prefix')

            # Handling for the default category
            if not guild_info[0]:
                await context.send("No category to put the new channel in specified, the channel will end up somewhere on the server. Notify someone administrating the server to move it if it's an issue and tell them to set the default category using the `{}admin set Start_category` command.".format(config.mod))
                category = None
            else:
                category = discord.utils.find(lambda c: c.id == guild_info[0], context.message.guild.categories)

            # Handling for the default completion role
            if not guild_info[1]:
                await context.send("No main game specified. People who have finished the game for this server won't be able to view the new channels. Notify someone administrating the server to add the completion role to the channel manunally and tell them to set the main game for the server using the `{}admin set Main_Game` command.".format(config.mod))
                main_game_role = None
                channel_suffix = 'game'
            else:
                self.client.cursor.execute("SELECT Role_Name, Channel_suffix FROM Game WHERE Name = ?", (guild_info[1],))
                game = self.client.cursor.fetchone()
                role_name = game[0]
                print(role_name)
                channel_suffix = game[1]
                main_game_role = modules.roles.Roles(self.client).find(role_name, context)
                if main_game_role is None:
                    await context.send("The completion role {} for this game is not present in the server! Please let some administrator to create it. For this channel no permissions for those who have completed the game will be applied.".format(role_name))
            
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
            overwrites.update(self.set_chapter_perms(12, context, True))
            # chapter permission update based on user's roles
            for role in context.message.author.roles:
                if re.match("{} \d+".format(guild_info[2]), role.name):
                    overwrites.update(self.set_chapter_perms(int(re.search('\d+', role.name).group()), context, False))
                    break
            
            # Creating the channel and setting the category
            channel = await context.message.guild.create_text_channel('{}-plays-{}'.format(name, channel_suffix), overwrites=overwrites, reason="New playthrough channel!")
            if category is not None:
                await channel.edit(category=category)

            # Saving to the database
            self.client.cursor.execute("INSERT INTO Channel (ID, Owner, Guild) VALUES (?, ?, ?)", (channel.id, context.message.author.id, context.message.guild.id,))
            self.client.database.commit()

            await context.send("Successfully created your playthrough channel! Have fun!")

    # Archiving a channel
    @commands.command(pass_context=True)
    async def end(self, context):
        channel = discord.utils.find(lambda c: c.id == self.owns(context), context.message.guild.text_channels)
        if channel is not None:
            archive_category = discord.utils.find(lambda c: c.id == self.fetch_guild_info(context, 'Archive_category')[0], context.message.guild.categories)
            if archive_category:
                await channel.edit(category=archive_category)
                await context.send("Archived your playthrough channel. Hope you had fun!")
            else:
                await context.send("No archive category set. Channel not archived. Let an administrator know that they should add an archiving category using the command `{}admin set Archive_category`".format(config.mod))
        else:
            context.send("You have not even started a playthrough yet! `{}end` is not if you have finished the game, use `{}finished` instead!.".format(config.mod, config.mod))

def setup(client):
    client.add_cog(Channel(client))
        