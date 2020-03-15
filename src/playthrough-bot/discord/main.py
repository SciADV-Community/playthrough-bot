#!env/bin/python3
"""Main module to run the bot."""
from discord.ext import commands
from maho import config, models, utils

# Logging
logger = utils.get_logger()

# Model setup
models.setup_tables()

# State
loaded_modules = []
client = commands.Bot(command_prefix=config.PREFIX, description=config.DESCRIPTION)


@client.event
async def on_ready():
    """Handle what happens when the bot is ready."""
    print(f"Logged in as {client.user.name} - {client.user.id}")

    print(f"------ Guilds ({len(client.guilds)}) ------")
    for guild in client.guilds:
        print(guild.name)

    print(f"------ Loading Modules ({len(config.STARTUP)}) ------")
    for module in config.STARTUP:
        if await utils.load_module(client, module):
            loaded_modules.append(module)


# Commands
@client.command(pass_context=True)
async def load(context, module: str = None):
    """Load a module."""
    if not module:
        await context.send("Load requires the name of the module to load.")
    elif module not in loaded_modules:
        if await utils.load_module(client, module, context):
            loaded_modules.append(module)
    else:
        await context.send(f"Module {module} already loaded.")


# Unloading a module
@client.command(pass_context=True)
async def unload(context, module: str = None):
    """Unload a module."""
    if not module:
        await context.send("Unload requires the name of the module to unload.")
    elif module in loaded_modules:
        if await utils.unload_module(client, module, context):
            loaded_modules.remove(module)
    else:
        await context.send(f"Module {module} not loaded.")


# Reloading a module
@client.command(pass_context=True)
async def reload(context, module: str = None):
    """Reload a module."""
    if module:
        if module in loaded_modules:
            if await utils.unload_module(
                client, module, context
            ) and await utils.load_module(client, module, context):
                await context.send(f"{module} reload complete.")
        else:
            await context.send(f"Module {module} not loaded.")
    else:
        for module in loaded_modules:
            unloaded = await utils.unload_module(client, module, context)
            if unloaded:
                await utils.load_module(client, module, context)
        else:
            logger.warning(
                "Unauthorized user %s attempted to reload all modules.",
                context.author.username,
            )


@client.event
async def on_message(message):
    """Handle new messages."""
    if message.author is not client:
        await client.process_commands(message)


@client.event
async def on_command_error(context, error):
    """Handle error-handling from commands."""
    command = context.message.content.split()[0][1:]
    logger.error("Error occured for command %s: %s", command, error)


# Running the client
client.run(config.TOKEN)