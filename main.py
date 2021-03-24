import discord, os, random, json, math
from simpleeval import simple_eval
from dotenv import load_dotenv
from discord.ext import commands
from replit import db


# Determine the number of dice, their sides, and if vantage is called
def get_dice(setup):
    vantage = False
    setup = setup.lower()

    if setup == None:
        dice, sides = 1, 20
    elif 'adv' in setup or 'dis' in setup:
        dice, sides = 2, 20
        vantage = True
    elif 'd' in setup:
        temp = (setup).split('d')
        dice = int(temp[0])
        sides = int(temp[1])
    elif 'perc' in setup:
        dice, sides = 1, 100
    else:
        dice, sides = 1, 20

    return dice, sides, vantage


# Returns the total from dice rolls plus a modifier
def get_total(total, mod):
    mod = '' if '1d' in mod.lower() else mod
    return math.floor(simple_eval(total + mod))


# Rolls a set number of n-sided dice with an option to reroll numbers if desired
def roll_dice(dice, sides, reroll=0):
    rolls = []
    for _ in range(dice):
        temp = random.randint(1, sides)
        if temp < reroll:
            temp = random.randint(1, sides)
        rolls.append(temp)
    return rolls


# Grabs a response from a JSON file of responses
def get_response(category="start"):
    return random.choice(db[category])


# Checks the total for funny numbers
def check_nice(total):
    quips = db['nice']
    return quips[total] if total in quips.keys() else ''


# Outputs the dice rolls
def get_rolls(mod, tail, dice, sides):
    if tail == None:
        rolls = roll_dice(dice, sides)
    elif mod.lower() == 'reroll':
        rolls = roll_dice(dice, sides, int(tail.split(' ', 1)[0]))
    elif 'reroll' in tail.lower():
        tail = tail.lower()
        temp = tail.replace('reroll ', '')
        if ' ' in temp:
            temp = int(temp.split(' ', 1)[0])
        else:
            temp = int(temp)
        rolls = roll_dice(dice, sides, temp)
    else:
        rolls = roll_dice(dice, sides)

    return rolls


# Checks if a Nat 20 or Nat 1
def get_vantage(content, rolls):
    response = ''
    content = content.lower()
    if 'adv' in content:
        if 20 == max(rolls):
            response += get_response('nat20')
        elif 1 == max(rolls):
            response += get_response('nat1')
    else:
        if 20 == min(rolls):
            response += get_response('nat20')
        elif 1 == min(rolls):
            response += get_response('nat1')
    return response


# Makes sure responses are less than 2000 characters for Discord
def check_size(text, total):
    if len(text) > 2000:
        response = get_response('end').format(total) + check_nice(total)
    else:
        response = text + get_response('end').format(total) + check_nice(total)
    return response


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_GUILD'))

bot = commands.Bot(command_prefix='$', case_insensitive=True)
bot.remove_command('help')


# Outputs a ready message to console when bot is online
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=GUILD)
    print(f'{bot.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')


# Fills the DB with data from a JSON file if on the testing server
@bot.command()
async def fill_db(ctx):
    guild = discord.utils.get(bot.guilds, id=GUILD)

    if guild.id == GUILD:
        response = 'Filling DB'
        with open('responses.json') as f:
            temp = json.load(f)

        for key in temp.keys():
            db[key] = temp[key]
    else:
        response = 'You do not have permission to do that.'

    await ctx.send(response)


# Manipulates the DB of responses if on the testing server
@bot.command(name='db')
async def mess_with_db(ctx, command, key: str = None, *, text: str = None):
    keyed = True if key != None else False
    guild = discord.utils.get(bot.guilds, id=GUILD)

    if guild.id == GUILD:
        if command == 'keys':
            response = list(db.keys())
        elif command == 'values' and keyed:
            response = db[key]
        elif command == 'delete' and keyed:
            temp = db[key]
            if text in temp:
                temp.remove(text)
                db[key] = temp
            response = 'Removed: {}'.format(text)
        elif command == 'add' and keyed:
            temp = db[key]
            temp.append(text)
            db[key] = temp
            response = 'Added: {}'.format(text)
        else:
            response = 'No valid command detected. Please try again.'
    else:
        response = 'You do not have permission to do that.'

    await ctx.send(response)


# Displays an embedded help doc for users
@bot.command()
async def help(ctx):
    text = ''
    with open('help.txt') as f:
        for line in f:
            text += line
    embed = discord.Embed(title='Raleigh Commands',
                          description=text,
                          color=discord.Color.red())
    await ctx.send(embed=embed)


# Flips a coin
@bot.command(name='flip')
async def flip_coin(ctx):
    response = random.choice(['Heads', 'Tails'])
    await ctx.send(response)


# Does math using a safer eval message
@bot.command()
async def calculate(ctx, *, message: str):
    await ctx.send(simple_eval(message))


# Rolls 7 sets of 4d6 dropping the lowest roll
@bot.command()
async def character(ctx):
    stats = []

    for _ in range(6):
        rolls = roll_dice(4, 6)
        rolls.remove(min(rolls))
        stats.append(sum(rolls))

    text = get_response('stats')
    text += ', '.join(list(map(str, stats)))

    mulligan = roll_dice(4, 6)
    mulligan.remove(min(rolls))
    text += get_response('mulligans').format(sum(mulligan))

    await ctx.send(text)


# Rolls a set of dice corresponding to a specific healing potion
# TODO Figure out a way to have users add custom potions to this command
@bot.command()
async def potion(ctx, *, drink=None):
    potions = {
        'healing': [2, 2],
        'standard': [2, 2],
        'greater': [4, 4],
        'superior': [8, 8],
        'supreme': [10, 20],
    }
    if drink != None and drink.lower() in potions:
        temp = potions[drink.lower()]
    else:
        temp = [2, 2]

    hp = sum(roll_dice(temp[0], 4)) + temp[1]
    response = get_response('health').format(hp)

    await ctx.send(response)


# The meat of the bot
@bot.command()
async def roll(ctx, setup: str = None, mod: str = None, *, tail: str = None):
    check_words = ['secret', 'perc', 'percentile', 'percentiles', 'reroll']

    # Determine the number of dice, their sides, and if vantage is called
    dice, sides, vantage = get_dice(setup)

    # Gets the dice rolls needed
    rolls = get_rolls(mod, tail, dice, sides)

    # Starts assembling a response
    text = get_response() + ' '
    text_rolls = ', '.join(list(map(str, rolls)))
    response = text + text_rolls

    if not vantage:
        if len(rolls) > 1:
            total = str(sum(rolls))
            if mod != None and mod not in check_words:
                total = get_total(total, mod)
            response = check_size(response, total)

        elif setup != None and setup not in check_words:
            if mod != None and mod not in check_words:
                total = get_total(text_rolls, mod)
            else:
                total = get_total(text_rolls, setup)

            if '1d' not in setup.lower():
                response = check_size(response, total)
            elif mod != None and mod not in check_words:
                response = check_size(response, total)
    else:
        response += get_vantage(ctx.message.content, rolls)

    if 'secret' in ctx.message.content.lower():
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(response)
        await ctx.send(get_response('secret'))
    else:
        await ctx.send(response)


bot.run(TOKEN)

bot.run(TOKEN)
