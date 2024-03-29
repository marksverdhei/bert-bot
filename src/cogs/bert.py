import discord
from discord import app_commands
from discord.ext import commands

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

nor_tokenizer = BertTokenizer.from_pretrained("ltgoslo/norbert2")
nor_tokenizer.unique_no_split_tokens.extend(nosplit_tokens)
nor_model = BertForMaskedLM.from_pretrained("ltgoslo/norbert2")
nor_mask_id = nor_tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
nor_stopword_ids = stopwords.get_stopword_ids(nor_tokenizer, stopwords.norwegian, cased=True)
nor_model.eval()
# #


def get_topn(content, tokenizer, model, mask_id, n, stopwords=None, bold=True):
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

            if bold:
                for s in substitutions:
                    yield f"**{s}**"
            else:
                yield from substitutions


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


def make_padded_result_message(results):
    max_space = [max(len(row[i]) for row in results) for i in range(len(results[0]))]
    results_padded = [[s + " " * (max_space[i]-len(s)) for i, s in enumerate(row)] for row in results]
    message = "\n".join("`" + (" | ".join(i for i in r)) + "`" for r in results_padded)
    return message


async def no_mask_error(interaction: discord.Interaction):
    embed = discord.Embed(
        color=discord.Color.gold(),
        description="⚠ Invalid call signature. Must include a `[MASK]` or `_`"
    )
    embed_templates.default_footer_interaction(interaction, embed)
    await interaction.response.send_message(embed=embed)


class Bert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    bert = app_commands.Group(name="bert", description="English BERT model commands")
    norbert = app_commands.Group(name="norbert", description="Norwegian BERT model commands")

    @bert.command(name="top", description="Get the top-n substitutes for the masked token")
    async def bert_top(self, interaction: discord.Interaction, number_of_suggestions: app_commands.Range[int, 1, 20], content: str):
        """
        Get the top-n substitutes for the masked token

        `[content...]` - Text input. Bert will suggest words where `_` is found.

        """
        results = []
        for i, s in enumerate(get_topn(content, tokenizer, model, mask_id, number_of_suggestions, stopwords=stopword_ids, bold=False)):
            i = i % number_of_suggestions
            if len(results) == i:
                results.append([f"{i+1}: {s}"])
            else:
                results[i].append(s)

        message = make_padded_result_message(results)

        if not message:
            return await no_mask_error(interaction)

        await interaction.response.send_message(message)

    @bert.command(name="insert", description="Make BERT fill in words marked with `_` in a given text")
    async def bert_insert(self, interaction: discord.Interaction, content: str):
        """
        Make Bert fill in words in a given text.

        `[content...]` - Text input. Bert will fill in words where `_` is found.
        """
        result = insert(tokenizer, model, mask_id, content, stopwords=stopword_ids)

        if not result or result == content:
            return await no_mask_error(interaction)

        await interaction.response.send_message(result)

    @norbert.command(name="top", description="Get the top-n substitutes for the masked token")
    async def norbert_top(self, interaction: discord.Interaction, number_of_suggestions: app_commands.Range[int, 1, 20], content: str):
        """
        Get the top-n substitutes for the masked token

        `[content...]` - Text input. Bert will suggest words where `_` is found.

        """
        results = []
        for i, s in enumerate(get_topn(content, nor_tokenizer, nor_model, nor_mask_id, number_of_suggestions, stopwords=nor_stopword_ids, bold=False)):
            i = i % number_of_suggestions
            if len(results) == i:
                results.append([f"{i+1}: {s}"])
            else:
                results[i].append(s)

        message = make_padded_result_message(results)

        if not message:
            return await no_mask_error(interaction)

        await interaction.response.send_message(message)

    @norbert.command(name="insert", description="Make NorBERT fill in words marked with `_` in a given text")
    async def norbert_insert(self, interaction: discord.Interaction, content: str):
        """
        Make Bert fill in words marked with `_` in a given text.

        `[content...]` - Text input. Bert will suggest words where `_` is found.
        """
        result = insert(nor_tokenizer, nor_model, nor_mask_id, content, stopwords=nor_stopword_ids)

        if not result or result == content:
            return await no_mask_error(interaction)

        await interaction.response.send_message(result)


async def setup(bot):
    await bot.add_cog(Bert(bot))
