#!python3
import discord, asyncio, sqlite3, config
from discord.ext import commands

class Help():
    ### Fields ###
    def __init__(self, client):
        self.client = client
        print("Module {} loaded".format(self.__class__.__name__))

    ### Helper Functions ###
    def get_cmd(self, cmd):
        self.client.cursor.execute("SELECT * FROM Command WHERE Name = ?", (cmd,))
        return self.client.cursor.fetchone()

    def get_args(self, cmd):
        self.client.cursor.execute("SELECT * FROM Argument WHERE Command = ?", (cmd,))
        return self.client.cursor.fetchall()

    ### Commands ###
    @commands.command(pass_context=True)
    async def help(self, context, command: str = None):
        if command is not None:
            # Querying the db for the command
            cmd = self.get_cmd(command)
            if cmd: # If it exists
                # Fetching the info
                name, description, example = cmd
                example = config.mod + example
                args = self.get_args(command)
                # Creating the embed
                embed = discord.Embed(title=name, colour = 0x42c6ff)

                if args:
                    arg_string = ""
                    for i in range(0, len(args)): 
                        arg_string += args[i][1]
                        if i != len(args) - 1: arg_string += ", "
                else:
                    arg_string = "No Arguments"

                embed.add_field(name="Arguments: ", value=arg_string)
                embed.add_field(name="Description: ", value=description)
                embed.add_field(name="Example: ", value=example)
                await context.send(embed=embed)
            else:
                await context.send("Command {} not found.".format(command))
        else:
            embed = discord.Embed(title="Commands", colour = 0x42c6ff)
            embed.add_field(name="Description: ", value="Here are all of the available commands. You should do `{}help <command>` to view more on a specific command.".format(config.mod))

            self.client.cursor.execute("SELECT Name FROM Command")
            commands = self.client.cursor.fetchall()

            cmds_str = ""
            for comm in commands:
                cmds_str += comm[0] + "\n"

            embed.add_field(name="List: ", value=cmds_str)

            await context.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))
