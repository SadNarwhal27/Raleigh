import os, discord
from dotenv import load_dotenv
from dice import get_rolls, get_dice
from checks import get_response
from utils import embed_maker, six_nine

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '$roll' in message.content:
        await message.channel.send(embed=roll(message))

    if message.content == '$69':
        await message.channel.send(six_nine())


def roll(ctx):
    # Starts assembling a response
    text = get_response() + ' '
    dice, sides = get_dice(ctx.content.strip('$roll '))
    total = get_rolls('', None, dice, sides)
    modifier = ''
    simple = False
    quip = ''
    gif = ''

    embed = embed_maker(text, total, 
                        ctx.author.display_name,
                        ctx.author.avatar, 
                        quip, gif)
    return embed


client.run(token)
