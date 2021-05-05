from discord.ext import commands
import discord

from time import time

from cogs.utils import embed_templates


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def uptime(self, ctx):
        """
        Fetches the amount of time the bot has been running for
        """

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='🔌 Uptime', value=await self.get_uptime())
        embed_templates.default_footer(ctx, embed)
        await ctx.reply(embed=embed)

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

        return f'{days}d, {hours}h, {minutes}m, {seconds}s'


def setup(bot):
    bot.add_cog(Misc(bot))
