#!python3
import discord, asyncio, config, modules.game
from discord.ext import commands

class Admin():
    ### Fields ###
    def __init__(self, client):
        self.client = client
        print("Module {} loaded".format(self.__class__.__name__))

    ### Helper Functions ###
    # Set a field in the config
    async def set(self, field, value, context):
        # Field validation
        valid = True

        if field != 'Guild_ID':
            if field == 'Main_Game':
                game = modules.game.Game(self.client).fetch_game(value)
                if game is None:
                    await context.send("Game {} not found".format(value))
                    valid = False
            elif field == "Archive_category" or field == "Start_category":
                if discord.utils.find(lambda c: c.id == value, context.message.guild.categories) is None:
                    await context.send("No category with such ID exists.")
                    valid = False
            elif field != "Guild_Name" and field != "Chapter_prefix" and field != "Route_prefix":
                valid = False
                await context.send("No such field in the table")

        else:
            valid = False

        if valid:
            query = "UPDATE Config SET {} = ? WHERE Guild_ID = ?".format(field)
            self.client.cursor.execute(query, (value,context.message.guild.id,))
            self.client.database.commit()
            await context.send("Successfully set {} to {}".format(field, value))

    def is_admin(self, context):
        ret = False

        for role in context.message.author.roles:
                if role.permissions.manage_roles: ret = True

        return ret
    
    ### Command ###
    @commands.command(pass_context=True)
    async def admin(self, context, cmd: str, field: str, *, arg: str):
        if self.is_admin(context):
            if cmd == 'set':
                await self.set(field, arg, context)
            else:
                await context.send("Invalid parameter")
        else:
            await context.send("You do not have the necessary perms (manage roles).")

def setup(client):
    client.add_cog(Admin(client))