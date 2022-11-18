import discord
from discord import app_commands
from discord.ext import commands

import traceback
import sys

from datetime import datetime


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """
        Prints command execution metadata
        """
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | " +
            f"{'❌ ' if ctx.command_failed else '✔ '} {ctx.command} - " +
            f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})"
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #  Ignore if command has its own error handling
        if hasattr(ctx.command, "on_error"):
            return

        #  Ignored errors
        ignored = commands.CommandNotFound
        error = getattr(error, "original", error)
        if isinstance(error, ignored):
            return

        send_help = (
            commands.MissingRequiredArgument,
            commands.TooManyArguments,
            commands.BadArgument
        )
        if isinstance(error, send_help):
            self.bot.get_command(f"{ctx.command}").reset_cooldown(ctx)
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.NotOwner):
            return await ctx.reply("This command can only be executed by a bot owner.")

        #  Print full exception to console
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr
        )

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command | app_commands.ContextMenu
    ):
        """
        Logs slash command execution metadata
        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        command (app_commands.Command | app_commands.ContextMenu): Command object
        """
        print(
            f"{'❌ ' if interaction.command_failed else '✔ '} {command.name} | " +
            f"{interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id}) | " +
            f"{interaction.guild_id}-{interaction.channel_id}-{interaction.id}"
        )

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle slash command errors
        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        error (app_commands.AppCommandError): Eror context object
        """
        await self.on_app_command_completion(interaction, interaction.command)  # Print command usage, just in case

        #  Print full exception to console
        print(f"Ignoring exception in command {interaction.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr
        )


async def setup(bot):
    await bot.add_cog(Errors(bot))
