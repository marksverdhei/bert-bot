from discord.ext import commands
import discord

from dotenv import load_dotenv
import os
from time import time


load_dotenv()

intents = discord.Intents.all()
mentions = discord.AllowedMentions(
    everyone=False,
    replied_user=False,
    users=False,
    roles=False
)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
            case_insensitive=True,
            allowed_mentions=mentions,
            intents=discord.Intents.default(),
            help_command=None
        )

        self.source_code_url = os.getenv("SOURCE_CODE_URL")


bot = Bot()


@bot.event
async def on_ready():
    if not hasattr(bot, "uptime"):
        bot.uptime = time()

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"cogs.{name}")

    print("-" * 50)
    print(f"{bot.user.name} has connected to Discord!")
    print("-" * 50)
    await bot.change_presence(
        activity=discord.Activity(type=3, name=os.getenv("ACTIVITY_MESSAGE")),
        status=discord.Status.online
    )


bot.run(os.getenv("DISCORD_TOKEN"), reconnect=True)
