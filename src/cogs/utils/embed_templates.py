def default_footer(ctx, embed):
    return embed.set_footer(icon_url=ctx.author.avatar_url, text=f"{ctx.author.name}#{ctx.author.discriminator}")
