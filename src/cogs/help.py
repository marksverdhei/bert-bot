from discord.ext import commands
import discord

from cogs.utils import embed_templates


class HelpCommand(commands.MinimalHelpCommand):
    async def filter_command(self, command: commands.Command) -> bool:
        """
        Filters commands that fails check decorators. Also filters disabled commands

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The Discord context
        command (discord.ext.commands.Command): The Discord command object

        Returns
        ----------
        bool: Whether or not the command is executable and viewable based on Discord context.
        """

        try:
            return await command.can_run(self.context)
        except commands.CommandError:
            return False

    def get_command_signature(self, command: commands.Command) -> str:
        """
        Documents what parameters are required and how to execute a command

        Parameters
        ----------
        command (discord.ext.commands.Command): The Discord command object

        Returns
        ----------
        str: A string showing command usage.
        """

        signature = f' {command.signature}' if command.signature else ''
        return f'{self.clean_prefix}{command.qualified_name}{signature}'

    async def send_bot_help(self, mapping):
        destination = self.get_destination()

        for cog, commandlist in mapping.items():
            if not commandlist or cog == self.cog:
                continue
            embed = discord.Embed(color=self.context.me.color, title=cog.qualified_name)
            embed.set_author(name=self.context.me.name, icon_url=self.context.me.avatar_url)
            embed_templates.default_footer(self.context, embed)
            for command in commandlist:
                if not command.hidden and await self.filter_command(command):
                    embed.add_field(name=command.name, value=command.help, inline=False)

            if embed.fields:
                await destination.send(embed=embed)

    async def send_cog_help(self, cog):
        destination = self.get_destination()

        embed = discord.Embed(color=self.context.me.color, title=cog.qualified_name)
        embed.set_author(name=self.context.me.name, icon_url=self.context.me.avatar_url)
        embed_templates.default_footer(self.context, embed)

        for command in cog.get_commands():
            if not command.hidden and await self.filter_command(command):
                embed.add_field(name=command.name, value=command.help, inline=False)

        if embed.fields:
            await destination.send(embed=embed)

    async def send_group_help(self, group):
        destination = self.get_destination()

        embed = discord.Embed(color=self.context.me.color, title=group.qualified_name)
        embed.set_author(name=self.context.me.name, icon_url=self.context.me.avatar_url)
        embed_templates.default_footer(self.context, embed)

        for command in group.commands:
            if not command.hidden and await self.filter_command(command):
                embed.add_field(
                    name=command.name,
                    value=f'```{self.get_command_signature(command)}```\n{command.help}',
                    inline=False
                )

        if embed.fields:
            await destination.send(embed=embed)

    async def send_command_help(self, command):
        destination = self.get_destination()

        embed = discord.Embed(color=self.context.me.color)
        embed.description = f'```{self.get_command_signature(command)}```\n{command.help}'
        embed.set_author(name=self.context.me.name, icon_url=self.context.me.avatar_url)
        embed_templates.default_footer(self.context, embed)
        await destination.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        """
        Falls back to default discord.py help message when cog is unloaded.
        """

        self.bot.help_command = self._original_help_command


async def setup(bot):
    await bot.add_cog(Help(bot))
