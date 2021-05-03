# bot.py
from discord.ext import commands
import discord

from dotenv import load_dotenv
import os


load_dotenv()


mentions = discord.AllowedMentions(
    everyone=False,
    replied_user=False
)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=os.getenv("PREFIX"), case_insensitive=True, allowed_mentions=mentions)


bot = Bot()


@bot.event
async def on_ready():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            name = file[:-3]
            bot.load_extension(f'cogs.{name}')

    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(
        activity=discord.Activity(type=3, name=os.getenv("ACTIVITY_MESSAGE")),
        status=discord.Status.online
    )


bot.run(os.getenv("DISCORD_TOKEN"), bot=True, reconnect=True)
