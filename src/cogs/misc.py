from discord.ext import commands


class Misc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		await ctx.send("Pong!")


def setup(bot):
	bot.add_cog(Misc(bot))
