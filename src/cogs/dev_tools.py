from discord.ext import commands
import discord

from os import system, listdir
from git import Repo


class DevTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def update(self, ctx):
        """
        Pull latest changes from github and reload cogs
        """

        await ctx.trigger_typing()

        system("git pull")

        for file in listdir("./cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.bot.unload_extension(f"cogs.{name}")

        for file in listdir("./cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.bot.load_extension(f"cogs.{name}")

        githash = Repo("../").head.commit

        embed = discord.Embed(color=ctx.me.color, description="✅ Done!")
        embed.add_field(name="Current commit hash", value=f"[{githash}]({self.bot.source_code_url}/commit/{githash})")
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def pull(self, ctx):
        """
        Pull latest changes from github
        """

        await ctx.trigger_typing()

        system("git pull")
        githash = Repo("../").head.commit

        embed = discord.Embed(color=ctx.me.color, description="✅ Done!")
        embed.add_field(name="Current commit hash", value=f"[{githash}]({self.bot.source_code_url}/commit/{githash})")

    @commands.is_owner()
    @commands.command()
    async def reloadall(self, ctx):
        """
        Reload all cogs
        """

        await ctx.trigger_typing()

        for file in listdir("./cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.bot.reload_extension(f"cogs.{name}")

        embed = discord.Embed(color=ctx.me.color, description="✅ Done!")
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(DevTools(bot))
