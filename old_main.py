import discord, os
from dice import get_dice, get_total, get_rolls
from admin import db_change, db_fill
from checks import get_response, check_nice, get_vantage, check_nats
from dnd import make_character, drink_potion
from utils import get_help, get_flip, get_math, six_nine, embed_maker
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = int(os.environ['DISCORD_GUILD'])

bot = commands.Bot(command_prefix='$', case_insensitive=True, intents=intents)
bot.remove_command('help')


# Outputs a ready message to console when bot is online
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=GUILD)
    print(f'{bot.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')


# Stops spam messages from showing up in the console
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, discord.HTTPException):
        print(error)
    raise error


# Fills the DB with data from a JSON file if on the testing server
@bot.command()
async def fill_db(ctx):
    guild = discord.utils.get(bot.guilds, id=GUILD)
    await ctx.send(db_fill(guild, GUILD))


# Manipulates the DB of responses if on the testing server
@bot.command(name='db')
async def mess_with_db(ctx, command, key: str = None, *, text: str = None):
    guild = discord.utils.get(bot.guilds, id=GUILD)
    await ctx.send(db_change(command, key, text, guild, GUILD))


# Displays an embedded help doc for users
@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Raleigh Commands',
                          description=get_help(),
                          color=discord.Color.red())
    await ctx.send(embed=embed)


# Flips a coin
@bot.command(name='flip')
async def flip_coin(ctx):
    await ctx.send(get_flip())


# Does math using a safer eval message
@bot.command()
async def calculate(ctx, *, message: str):
    await ctx.send(get_math(message))


# A dumb command for dumb responses
# Turn this into an embed
@bot.command(name='69')
async def sixty_nine(ctx):
    await ctx.send(embed=six_nine())


# Rolls 7 sets of 4d6 dropping the lowest roll
# Turn this into an embed
@bot.command()
async def character(ctx):
    await ctx.send(make_character())


# Rolls a set of dice corresponding to a specific healing potion
# Turn this into an embed
@bot.command()
async def potion(ctx, *, drink=None):
    await ctx.send(drink_potion(drink))


# The meat of the bot
# TODO Put this in its own script for code management
@bot.command()
async def roll(ctx, setup: str = None, mod: str = None, *, tail: str = None):
    check_words = [
        'secret', 'perc', 'percentile', 'percentiles', 'reroll', 'simple'
    ]
    
    # Determine the number of dice, their sides, and if vantage is called
    dice, sides, vantage = get_dice(setup)

    # Gets the dice rolls needed
    rolls = get_rolls(mod, tail, dice, sides)
    rolls.insert(len(rolls) - 1, '&')
    text_rolls = ', '.join(list(map(str, rolls)))
    rolls.remove('&')
    if len(rolls) > 2:
        text_rolls = text_rolls.replace('&,', '&')
    elif len(rolls) == 2:
        text_rolls = text_rolls.replace(',', '')
    else:
        text_rolls = text_rolls.replace('&, ', '')

    # Starts assembling a response
    text = get_response() + ' '
    total = ''
    modifier = ''
    simple = False
    quip = ''
    gif = ''

    if not vantage:
        modded = True if mod != None and mod not in check_words else False
        simple = True if mod != None and (
            setup.lower() == 'simple' or mod.lower() == 'simple') else False

        if setup == None:
            pass
        elif len(rolls) > 1:
            total = str(sum(rolls))
            if modded:
                total = get_total(total, mod)
                modifier = ' ' + mod
        elif setup not in check_words:
            if modded:
                total = get_total(text_rolls, mod)
                modifier = ' ' + mod
            else:
                total = get_total(text_rolls, setup)

    if simple:
        text += text_rolls
        text_rolls = ' '
    elif total == '':
        if vantage:
            quip, gif, focus = get_vantage(ctx.message.content, rolls)
            text += focus
        else:
            text += text_rolls
            quip, gif = check_nats(max(rolls))
    else:
        text += str(total)
        quip = check_nice(total)
    text_rolls += modifier

    if 'secret' in ctx.message.content.lower():
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(
            embed=embed_maker(text, text_rolls, ctx.author.display_name,
                              ctx.author.avatar_url, quip))
        await ctx.send(get_response('secret'))
    else:
        await ctx.send(
            embed=embed_maker(text, text_rolls, ctx.author.display_name,
                              ctx.author.avatar_url, quip, gif))


bot.run(TOKEN)
