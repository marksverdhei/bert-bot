import discord
from discord import app_commands
from discord.ext import commands

from time import time
import platform
from os import getpid, environ
from psutil import Process
from git import Repo

from cogs.utils import embed_templates


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.command()
    async def botinfo(self, interaction: discord.Interaction):
        """
        Displays key information about the bot
        """
        dev = await self.bot.fetch_user(142720616661909504)
        invite_link = "https://discordapp.com/oauth2/authorize?client_id=" + \
                      f"{self.bot.user.id}&permissions=378944&scope=bot"

        # Memory usage
        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)

        # Build embed
        embed = discord.Embed(url=self.bot.source_code_url, title=self.bot.user.name)
        embed.set_author(name=dev.name, icon_url=dev.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.add_field(name="Dev", value=f"{dev.mention}\n{dev.name}#{dev.discriminator}", inline=False)
        embed.add_field(name="Uptime", value=await self.get_uptime(), inline=False)
        embed.add_field(
            name="Websocket Ping",
            value=f"{int(self.bot.latency * 1000)} ms",
            inline=False
        )
        embed.add_field(
            name="Stats",
            value=f"{len(self.bot.users)} users\n{len(self.bot.guilds)} guilds",
            inline=False
        )
        embed.add_field(
            name="Software",
            value=f"Discord.py {discord.__version__}\nPython {platform.python_version()}",
            inline=False
        )
        embed.add_field(name="RAM Usage", value=f"{memory_usage} MB", inline=False)
        embed.add_field(name="Kernel", value=f"{platform.system()} {platform.release()}", inline=False)
        if "docker" in environ:
            embed.add_field(name="Docker", value="U+FE0F", inline=False)
        embed.add_field(
            name="Links",
            value=f"[Source code]({self.bot.source_code_url}) | [Invite link]({invite_link})",
            inline=False
        )
        embed_templates.default_footer_interaction(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.command()
    async def uptime(self, interaction: discord.Interaction):
        """
        Fetches the amount of time the bot has been running for
        """
        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(name="🔌 Uptime", value=await self.get_uptime())
        embed_templates.default_footer_interaction(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.command()
    async def version(self, interaction: discord.Interaction):
        """
        Check version
        """
        githash = Repo("../").head.commit

        embed = discord.Embed(color=interaction.client.user.color, title="Git commit hash")
        embed.description = f"[{githash}]({self.bot.source_code_url}/commit/{githash})"
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.command()
    async def github(self, interaction: discord.Interaction):
        """
        Get source code url
        """
        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(
            name="🔗 Github Repo",
            value=f"[Click here]({self.bot.source_code_url}) to view my source code"
        )
        embed_templates.default_footer_interaction(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """
        Check if the bot is able to respond
        """
        await interaction.response.send_message("Pong!")

    async def get_uptime(self):
        """
        Returns the current uptime of the bot in string format
        """
        now = time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        return f"{days}d, {hours}h, {minutes}m, {seconds}s"


async def setup(bot):
    await bot.add_cog(Misc(bot))
