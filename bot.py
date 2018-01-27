#!python3
import sqlite3, asyncio, discord
from discord.ext import commands
import config, db_setup

#### Constant Definitions ###
modules = ["modules.roles", "modules.game", "modules.channel", "modules.admin", "modules.help"]
startup_modules = ["modules.roles", "modules.game", "modules.channel", "modules.admin", "modules.help"]
loaded_modules = []

### Setting up the Client / db ###
client = commands.Bot(command_prefix=config.mod, description=config.description)
client.database = sqlite3.connect(config.db + '.db')
client.cursor = client.database.cursor()
client.config = config
client.remove_command("help")
db_setup.table_setup(client)

### Helper functions ###
# Unloading a module
async def h_unload(client, module, context):
    try:
        if module in loaded_modules:
            loaded_modules.remove(module)
            client.unload_extension(module)
    except(AttributeError, ImportError) as e:
        error_str = "{} failed to unload: \n {}: {}".format(module, type(e).__name__, e)
        if context is not None:
            await context.send(error_str)
        else:
            print(error_str)

# Loading a module
async def h_load(client, module, context):
    try:
        client.load_extension(module)
    except(AttributeError, ImportError) as e:
        error_str = "{} failed to load: \n {}: {}".format(module, type(e).__name__, e)
        if context is not None:
            await context.send(error_str)
        else:
            print(error_str)

# Validating the user has perms
def allowed(client, user):
    return user.id == config.master

### Client Start Up ###
@client.event
async def on_ready():
    # Printing basic info to the console
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for guild in client.guilds:
        print(guild.name)
    print('------')
    # Loading the modules
    for module in startup_modules:
        await h_load(client, module, None)

### Joining a new server setup ###
@client.event
async def on_server_join(guild):
    # Add information about the server into the database
    client.cursor.execute('''
    INSERT INTO Config (Guild_ID, Guild_Name) VALUES ({0}, '{1}')
    '''.format(guild.id, guild.name))
    client.database.commit()

### Commands ###
# Loading a module
@client.command(pass_context=True)
async def load(context, module: str):
    await h_load(client, module, context)
    await context.send("{} loaded.".format(module))

# Unloading a module
@client.command(pass_context=True)
async def unload(context, module: str):
    await h_unload(client, module, context)
    await context.send("{} unloaded.".format(module))

# Reloading a module
@client.command(pass_context=True)
async def reload(context, module: str = None):
    if allowed(client, context.message.author):
        if module is not None:
            if module in modules:
                await h_unload(client, module, context)
                await h_load(client, module, context)
                await context.send("{} reloaded.".format(module))
            else:
                await context.send("{} not found.".format(module))
        else:
            for mod in modules:
                await h_unload(client, mod, context)
                await h_load(client, mod, context)
            await context.send("All modules reloaded")

### Message Handling ###
@client.event
async def on_message(message):
    if message.author is not client:
        await client.process_commands(message)

### Error Handling ###
@client.event
async def on_command_error(context, error):
    print(error)
    mod = config.mod
    if type(error).__name__ == 'MissingRequiredArgument':
        await context.send("Error: Not all required arguments were provided. Please review the details about the command you are trying to use, using `{}help {}`".format(mod, context.message.content.split()[0][1:]))

# Running the client
client.run(config.token)
# We are done with the database
client.database.close()