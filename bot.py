# bot.py
import os
from transformers import BertTokenizer, BertForMaskedLM
import torch
import discord
from dotenv import load_dotenv
import functools

# SET UP MODELS
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMaskedLM.from_pretrained("bert-base-uncased")
mask_id = tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
model.eval()

nor_tokenizer = BertTokenizer.from_pretrained("ltgoslo/norbert")
nor_model = BertForMaskedLM.from_pretrained("ltgoslo/norbert")
nor_mask_id = nor_tokenizer("[MASK]", add_special_tokens=False).input_ids[0]
nor_model.eval()
# #

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def get_topn(content, tokenizer, model, mask_id, n):
    tokens = tokenizer(content, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**tokens).logits.squeeze()
    mask_positions, = torch.where(tokens.input_ids[0] == mask_id)
    if not len(mask_positions):
        yield message.channel.send("Invalid call signature. Must include a [MASK]")
    else:
        preds = outputs[mask_positions]
        for pred in preds:
            topn = (-pred).squeeze().argsort()[:n]
            print(topn)
            substitutions = tokenizer.convert_ids_to_tokens(topn)
            for j, s in enumerate(substitutions):
                yield s

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    msg = message.content
    content = " ".join(msg.split(" ")[1:])
    if msg.startswith("!bert-mlm "):
        for i, s in enumerate(get_topn(content, tokenizer, model, mask_id, 5), start=1):
            await message.channel.send(f"{i}: {s}")

    elif msg.startswith("!bert-insert "):
        result = functools.reduce(
            (lambda x, y: x.replace("[MASK]", y, 1)),
            get_topn(content, tokenizer, model, mask_id, 1),
            content
        )
        await message.channel.send(result)


    elif msg.startswith("!norbert-mlm"):
        for i in get_topn(content, nor_tokenizer, nor_model, nor_mask_id, 5):
            await message.channel.send(i)

client.run(TOKEN)
