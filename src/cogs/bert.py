from discord.ext import commands
import discord

from transformers import BertTokenizer, BertForMaskedLM
import torch
import functools
import re
from cogs.utils import embed_templates, stopwords


# SET UP MODELS
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMaskedLM.from_pretrained("bert-base-uncased")
mask_id = tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
stopword_ids = stopwords.get_stopword_ids(tokenizer, stopwords.english, cased=False)
model.eval()

nor_tokenizer = BertTokenizer.from_pretrained("ltgoslo/norbert")
nor_model = BertForMaskedLM.from_pretrained("ltgoslo/norbert")
nor_mask_id = nor_tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
nor_stopword_ids = stopwords.get_stopword_ids(nor_tokenizer, stopwords.norwegian, cased=True)
nor_model.eval()
# #


def get_topn(content, tokenizer, model, mask_id, n, stopwords=None):
    content = re.sub("_+", "[MASK]", content)
    tokens = tokenizer(content, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**tokens).logits.squeeze()
    mask_positions, = torch.where(tokens.input_ids[0] == mask_id)


    if not len(mask_positions):
        yield ""
    else:
        preds = outputs[mask_positions]
        for pred in preds:
            sorted_logits = (-pred).squeeze().argsort()
            if stopwords is not None:
                places_where_stopword_id = ((sorted_logits == stopwords[:, None]).sum(0)).bool()
                places_where_not_stopword_id = places_where_stopword_id.logical_not()
                topn = sorted_logits[places_where_not_stopword_id][:n]
            else:
                topn = sorted_logits[:n]

            substitutions = tokenizer.convert_ids_to_tokens(topn)
            for j, s in enumerate(substitutions):
                yield f"**{s}**"


def insert(tokenizer, model, mask_id, content, stopwords=None):
    return functools.reduce(
        (lambda x, y: re.sub(r"(\[MASK\]|_+)", y, x, 1)),
        get_topn(content, tokenizer, model, mask_id, 1, stopwords=stopwords),
        content
    )


def get_mlm_message(tokenizer, model, mask_id, content, stopwords=None):
    message = ""
    for i, s in enumerate(get_topn(content, nor_tokenizer, nor_model, nor_mask_id, 5, stopwords=stopwords), start=1):
        if s:
            message += f"{i}: {s}\n"
    return message


async def no_mask_error(ctx):
    embed = discord.Embed(color=discord.Color.gold(), description="⚠ Invalid call signature. Must include a `[MASK]` or `_`")
    embed_templates.default_footer(ctx, embed)
    await ctx.reply(embed=embed)


class Bert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="bert")
    async def bert(self, ctx):
        """
        Bert commands
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @bert.command(name="mlm")
    async def mlm(self, ctx, *content):
        """
        Bert MLM
        """
        content = " ".join(content)
        message = get_mlm_message(tokenizer, model, mask_id, content, stopwords=stopword_ids)

        if not message:
            return await no_mask_error(ctx)

        await ctx.reply(message)

    @bert.command(name="insert")
    async def insert(self, ctx, *content):
        """
        Make Bert fill in words marked with [MASK] in sentences
        """
        content = " ".join(content)
        result = insert(tokenizer, model, mask_id, content, stopwords=stopword_ids)

        if not result or result == content:
            return await no_mask_error(ctx)

        await ctx.reply(result)

    @commands.group(name="norbert")
    async def norbert(self, ctx):
        """
        NorBert commands
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @norbert.command(name="mlm")
    async def normlm(self, ctx, *content):
        """
        NorBert MLM
        """
        content = " ".join(content)
        message = get_mlm_message(nor_tokenizer, nor_model, nor_mask_id, content, stopwords=nor_stopword_ids)

        if not message:
            return await no_mask_error(ctx)

        await ctx.reply(message)

    @norbert.command(name="insert")
    async def norinsert(self, ctx, *content):
        """
        Make Bert fill in words marked with [MASK] in sentences
        """
        content = " ".join(content)
        result = insert(nor_tokenizer, nor_model, nor_mask_id, content, stopwords=nor_stopword_ids)

        if not result or result == content:
            return await no_mask_error(ctx)

        await ctx.reply(result)


def setup(bot):
    bot.add_cog(Bert(bot))
