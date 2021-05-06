from discord.ext import commands
import discord

from time import time, perf_counter
import platform
from os import getpid, environ
from psutil import Process
from git import Repo

from cogs.utils import embed_templates


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=["info", "about"])
    async def botinfo(self, ctx):
        """
        Displays key information about the bot
        """

        dev = await self.bot.fetch_user(142720616661909504)
        invite_link = "https://discordapp.com/oauth2/authorize?client_id=" + \
                      f"{self.bot.user.id}&permissions=378944&scope=bot"

        # Ping
        start = perf_counter()
        status_msg = await ctx.send("Pinging...")
        end = perf_counter()
        ping = int((end - start) * 1000)

        # Memory usage
        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)

        # Build embed
        embed = discord.Embed(color=ctx.me.color, url=self.bot.source_code_url, title=self.bot.user.name)
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Dev", value=f"{dev.mention}\n{dev.name}#{dev.discriminator}", inline=False)
        embed.add_field(name="Uptime", value=await self.get_uptime(), inline=False)
        embed.add_field(
            name="Ping",
            value=f"Real: {ping} ms\nWebsocket: {int(self.bot.latency * 1000)} ms",
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
        embed_templates.default_footer(ctx, embed)
        await status_msg.edit(embed=embed, content=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def uptime(self, ctx):
        """
        Fetches the amount of time the bot has been running for
        """

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name="🔌 Uptime", value=await self.get_uptime())
        embed_templates.default_footer(ctx, embed)
        await ctx.reply(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def version(self, ctx):
        """
        Check version
        """

        githash = Repo("../").head.commit

        embed = discord.Embed(color=ctx.me.color, title="Git commit hash")
        embed.description = f"[{githash}]({self.bot.source_code_url}/commit/{githash})"
        await ctx.reply(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=["githubrepo", "repo", "git"])
    async def github(self, ctx):
        """
        Get source code url
        """

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(
            name="🔗 Github Repo",
            value=f"[Click here]({self.bot.source_code_url}) to view my source code"
        )
        embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply("Pong!")

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


def setup(bot):
    bot.add_cog(Misc(bot))
