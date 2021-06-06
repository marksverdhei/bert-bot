from discord.ext import commands
import discord

from transformers import BertTokenizer, BertForMaskedLM
import torch
import functools
import re
from cogs.utils import embed_templates, stopwords

nosplit_tokens = ["..."]
# SET UP MODELS
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
tokenizer.unique_no_split_tokens.extend(nosplit_tokens)
model = BertForMaskedLM.from_pretrained("bert-base-uncased")
mask_id = tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
stopword_ids = stopwords.get_stopword_ids(tokenizer, stopwords.english, cased=False)
model.eval()

nor_tokenizer = BertTokenizer.from_pretrained("ltgoslo/norbert")
nor_tokenizer.unique_no_split_tokens.extend(nosplit_tokens)
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
    result_string = functools.reduce(
        (lambda x, y: re.sub(r"(\[MASK\]|_+)", y, x, 1)),
        get_topn(content, tokenizer, model, mask_id, 1, stopwords=stopwords),
        content
    )
    result_string = re.sub(r"\s\*\*##", r"**##", result_string)
    result_string = re.sub("##", "", result_string)
    return result_string


def get_mlm_message(tokenizer, model, mask_id, content, stopwords=None):
    message = ""
    for i, s in enumerate(get_topn(content, tokenizer, model, mask_id, 5, stopwords=stopwords), start=1):
        if s:
            message += f"{i}: {s}\n"
    return message


async def no_mask_error(ctx):
    embed = discord.Embed(
        color=discord.Color.gold(),
        description="⚠ Invalid call signature. Must include a `[MASK]` or `_`"
    )
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


    @bert.command(name="top")
    async def top(self, ctx, *content):
        print(content)
        assert content[0].isdigit(), f"{content[0]} is not a digit"
        n = int(content[0])
        content = " ".join(content[1:])

        results = []
        for i, s in enumerate(get_topn(content, tokenizer, model, mask_id, n, stopwords=stopword_ids)):
            i = i%n
            print(i, s)
            if len(results) == i:
                results.append([f"{i+1}: {s}"])
            else:
                results[i].append(s)

        message = "\n".join("\t".join(i for i in r) for r in results)
        await ctx.reply(message)

    @bert.command(name="mlm")
    async def mlm(self, ctx, *content):
        """
        Get the top 5 suggested filler words for a given text.

        `[content...]` - Text input. Bert will suggest words where `_` is found.
        """
        content = " ".join(content)
        message = get_mlm_message(tokenizer, model, mask_id, content, stopwords=stopword_ids)

        if not message:
            return await no_mask_error(ctx)

        await ctx.reply(message)

    @bert.command(name="insert")
    async def insert(self, ctx, *content):
        """
        Make Bert fill in words in a given text.

        `[content...]` - Text input. Bert will fill in words where `_` is found.
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

    @norbert.command(name="top")
    async def top(self, ctx, *content):
        assert content[0].isdigit()
        n = int(content[0])
        content = " ".join(content[1:])

        results = []
        for i, s in enumerate(get_topn(content, nor_tokenizer, nor_model, nor_mask_id, n, stopwords=nor_stopword_ids)):
            i = i%n
            print(i, s)
            if len(results) == i:
                results.append([f"{i+1}: {s}"])
            else:
                results[i].append(s)

        message = "\n".join("\t".join(i for i in r) for r in results)
        await ctx.reply(message)

    @norbert.command(name="mlm")
    async def normlm(self, ctx, *content):
        """
        Get the top 5 suggested filler words for a given text.

        `[content...]` - Text input. Bert will suggest words where `_` is found.
        """

        content = " ".join(content)
        message = get_mlm_message(nor_tokenizer, nor_model, nor_mask_id, content, stopwords=nor_stopword_ids)

        if not message:
            return await no_mask_error(ctx)

        await ctx.reply(message)

    @norbert.command(name="insert")
    async def norinsert(self, ctx, *content):
        """
        Make Bert fill in words marked with `_` in a given text.

        `[content...]` - Text input. Bert will suggest words where `_` is found.
        """

        content = " ".join(content)
        result = insert(nor_tokenizer, nor_model, nor_mask_id, content, stopwords=nor_stopword_ids)

        if not result or result == content:
            return await no_mask_error(ctx)

        await ctx.reply(result)


def setup(bot):
    bot.add_cog(Bert(bot))
