import discord, os, random, json, math
from dotenv import load_dotenv
from discord.ext import commands


# Returns the total from dice rolls plus a modifier
def get_total(total, mod):
    return math.floor(eval(total + mod))


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
    with open('responses.json') as f:
        temp = json.load(f)
        responses = temp[category]
    return random.choice(responses)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_GUILD'))

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')


# Outputs a ready message to console when bot is online
@bot.event
async def on_ready():
    # Goes through every server the bot is in and finds the server you are working on that you set in .env
    guild = discord.utils.get(bot.guilds, id=GUILD)
    print(f'{bot.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')


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


# Does math
@bot.command()
async def calculate(ctx, *, message: str):
    await ctx.send(eval(message))


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
@bot.command()
async def potion(ctx, *, drink=None):
    potions = {
        'healing': [2, 2],
        'standard': [2, 2],
        'greater': [4, 4],
        'superior': [8, 8],
        'supreme': [10, 20],
    }
    if drink != None and drink in potions:
        temp = potions[drink]
    else:
        temp = [2, 2]

    hp = sum(roll_dice(temp[0], 4)) + temp[1]
    response = get_response('health').format(hp)

    await ctx.send(response)


# The meat of the bot
@bot.command()
async def roll(ctx, setup: str = None, mod: str = None, *, tail: str = None):
    check_words = ['secret', 'perc', 'percentile', 'percentiles', 'reroll']
    vantage = False

    if setup == None:
        dice, sides = 1, 20
    elif 'adv' in setup or 'dis' in setup:
        dice, sides = 2, 20
        vantage = True
    elif 'd' in setup:
        temp = setup.split('d')
        dice = int(temp[0])
        sides = int(temp[1])
    elif 'perc' in setup:
        dice, sides = 1, 100
    else:
        dice, sides = 1, 20

    if tail == None:
        rolls = roll_dice(dice, sides)
    elif mod == 'reroll':
        rolls = roll_dice(dice, sides, int(tail.split(' ', 1)[0]))
    elif 'reroll' in tail:
        temp = tail.replace('reroll ', '')
        if ' ' in temp:
            temp = int(temp.split(' ', 1)[0])
        else:
            temp = int(temp)
        rolls = roll_dice(dice, sides, temp)
    else:
        rolls = roll_dice(dice, sides)

    text = get_response() + ' '
    text_rolls = ', '.join(list(map(str, rolls)))
    response = text + text_rolls

    if not vantage:
        if len(rolls) > 1:
            total = str(sum(rolls))
            if mod != None and mod not in check_words:
                total = get_total(total, mod)
            response += get_response('end').format(total)

            if total == '69':
                response += '\nNice! 😊'
        elif setup != None and setup not in check_words:
            total = get_total(text_rolls, setup)
            response += get_response('end').format(total)

            if total == '69':
                response += '\nNice! 😊'
    else:
        if 'adv' in ctx.message.content:
            if 20 == max(rolls):
                response += get_response('nat20')
            elif 1 == max(rolls):
                response += get_response('nat1')
        else:
            if 20 == min(rolls):
                response += get_response('nat20')
            elif 1 == min(rolls):
                response += get_response('nat1')

    if 'secret' in ctx.message.content.lower():
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(response)
        await ctx.send(get_response('secret'))
    else:
        await ctx.send(response)


bot.run(TOKEN)
