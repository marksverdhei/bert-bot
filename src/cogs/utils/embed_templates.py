
import discord
from discord.ext import commands


def default_footer(ctx: commands.Context, embed: discord.Embed):
    return embed.set_footer(icon_url=ctx.author.avatar_url, text=f"{ctx.author.name}#{ctx.author.discriminator}")


def default_footer_interaction(interaction: discord.Interaction, embed: discord.Embed):
    return embed.set_footer(icon_url=interaction.user.avatar, text=f"{interaction.user.name}#{interaction.user.discriminator}")
