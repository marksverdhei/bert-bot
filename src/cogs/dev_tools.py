from discord.ext import commands

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

        for file in listdir('./cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.unload_extension(f'cogs.{name}')

        for file in listdir('./cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.load_extension(f'cogs.{name}')

        githash = Repo('../').head.commit

        await ctx.reply(f'Done!\n\nI\'m on commit hash `{githash}`')

    @commands.is_owner()
    @commands.command()
    async def pull(self, ctx):
        """
        Pull latest changes from github
        """

        await ctx.trigger_typing()
        
        system("git pull")
        githash = Repo('../').head.commit

        await ctx.reply(f'Done!\n\nI\'m on commit hash `{githash}`')

    @commands.is_owner()
    @commands.command()
    async def reloadall(self, ctx):
        """
        Reload all cogs
        """

        await ctx.trigger_typing()

        for file in listdir('./cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.reload_extension(f'cogs.{name}')

        await ctx.reply('Done!')


def setup(bot):
    bot.add_cog(DevTools(bot))