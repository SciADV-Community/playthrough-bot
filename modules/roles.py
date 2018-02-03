#!python3
import discord, asyncio, sqlite3, modules.channel
import config
from discord.ext import commands

class Roles:
    ### Fields ###
    def __init__(self, client):
        self.client = client
        print("Module {} loaded".format(self.__class__.__name__))

    ### Helper Functions ###
    # Find a role in the server
    def find(self, name, context):
        ret = None
        for role in context.guild.roles:
            if role.name == name: ret = role
        return ret

    # Find if an argument is a Chapter
    def isChapter(self, s):
        ret = True
        try: 
            int(s)
        except ValueError:
            ret = False
        return ret

    # Remove chapter roles
    async def strip_chapter_roles(self, context, prefix):
        for role in context.message.author.roles:
                if role.name.startswith(prefix):
                    await context.author.remove_roles(role)
                    break

    # Remove route ro les
    async def strip_route_roles(self, context, suffix):
        for role in context.message.author.roles:
            if role.name.endswith(suffix):
                await context.author.remove_roles(role)

    ### Commands ###
    # Handling Chapter / Route finishing
    @commands.command(pass_context=True)
    async def chapter(self, context, arg: str):
        # The difference between Chapter and Route is that routes are not completed linearly. Chapters are also numbered from 1 to whatever

        # Loading info from the config
        chapter_prefix, route_prefix = modules.channel.Channel(self.client).fetch_guild_info(context, 'Chapter_prefix', 'Route_prefix')

        # if we have a chapter
        if self.isChapter(arg):
            # remove previous chapter roles
            await self.strip_chapter_roles(context, chapter_prefix)
            match = chapter_prefix + ' {}' # String we are going to find a role with
            c = modules.channel.Channel(self.client) # To check if the user has a channel
            channel = discord.utils.find(lambda cha: cha.id == c.owns(context), context.message.guild.text_channels)
            if channel is not None: # if he has a channel
                overwrites = c.set_chapter_perms(int(arg), context, False) # Block permissions up until the chapter he just completed
                for role, perm in overwrites.items():
                    await channel.set_permissions(role, overwrite=perm)
                
        else: # If we have a route
            arg = arg.capitalize()
            match = '{} ' + route_prefix

        target_role = self.find(match.format(arg), context)
        if target_role is not None:
            await context.author.add_roles(target_role)
            await context.send("Successfully added the {} role.".format(target_role.name))
        else:
            await context.send("Role not found.")

    # Handling Game finishing
    @commands.command(pass_context=True)
    async def finished(self, context, *, game: str):
        # Getting the role for the game
        self.client.cursor.execute("SELECT Role_Name FROM Game JOIN Game_Alias ON Game.Name = Game_Alias.Game_Name WHERE Game.Name = ? OR Game_Alias.Alias = ?", (game, game,))
        role = self.client.cursor.fetchone()
        if role: # if it exists
            target_role = self.find(role[0], context)
            if target_role is not None: # If it exists in the server
                # Loading info from the config
                chapter_prefix, route_prefix = modules.channel.Channel(self.client).fetch_guild_info(context, 'Chapter_prefix', 'Route_prefix')
                # remove any other progression roles
                await self.strip_chapter_roles(context, chapter_prefix)
                await self.strip_route_roles(context, route_prefix)
                # add the new role
                await context.message.author.add_roles(target_role)
                await context.send("Successfully added the {} role.".format(target_role.name))
            else:
                await context.send("Role {} not found, which should not be the case. Contact someone who is administrating the server to add it.".format(role))
        else:
            await context.send("Game {} not found".format(game))

def setup(client):
    client.add_cog(Roles(client))