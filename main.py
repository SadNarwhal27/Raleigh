import discord, os, random, json


# Checks if the user requests a secret roll
def check_secret(command):
    if 'secret' in command:
        return True
    else:
        return False


# Makes sure the dice roll can be sent to the channel if the message is too large
def character_limiter(text):
    if len(text) >= 2000:
        return True
    else:
        return False


# Replaces substrings from a string
def strip_parts(word, stuff=' '):
    return word.replace(stuff, '')


# Grabs a response from a JSON file of responses
def get_response(category="start"):
    with open('responses.json') as f:
        temp = json.load(f)
        responses = temp[category]

    return random.choice(responses)


def check_reroll(command):
    temp = command.split("reroll ")
    if len(temp) == 1:
        temp.append('0')
    return temp


# Returns a or an depending on the number rolled for grammer's sake
def grammer(total):
    checks = [8, 11, 18, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]

    for i in range(800, 899):
        checks.append(i)

    if total in checks:
        return ' an '
    else:
        return ' a '


# Checks if the total comes out to something funny
def nice(total):
    with open("responses.json", "r") as f:
        temp = json.load(f)
        quotes = temp["nice"]

    if str(total) in quotes:
        text = quotes[str(total)]
    else:
        text = ''

    return text


# Checks if a d20 roll is a crit
def crit(roll):
    if roll == 20:
        return "\n" + get_response("nat20")
    elif roll == 1:
        return "\n" + get_response("nat1")
    else:
        return ''


# Returns a string of the rolls and totals
def stringify_rolls(rolls, mod):
    text = get_response()

    if type(rolls) != list:
        rolls = [rolls]

    text += grammer(rolls[0])

    for i in range(len(rolls)):
        if i == len(rolls) - 1:
            text += str(rolls[i])
        else:
            text += str(rolls[i]) + ', '
    text += ' ' + mod

    if mod == '':
        total = sum(rolls)
    else:
        total = sum(rolls) + get_mod(mod)

    # Checks if only 1 die is rolled
    if len(rolls) != 1:
        if character_limiter(text):
            text = get_response("end") + str(total)
        else:
            text += get_response("end") + str(total)
    elif len(rolls) == 1 and mod != '':
        text += get_response("end") + str(total)

    return text + nice(total)


# Rolls dice from inputs
def roll_dice(sides=20, num=1, reroll=0):
    if sides == 0 or num == 0:
        roll = 0
    elif num == 1:
        roll = random.randint(1, sides)
        if roll <= reroll:
            roll = random.randint(1, sides)
    else:
        roll = []
        for i in range(num):
            temp = random.randint(1, sides)
            if temp <= reroll:
                temp = random.randint(1, sides)
            roll.append(temp)
    return roll


# Returns an int modifier if one is given
def get_mod(word):
    word = strip_parts(word)
    if word.startswith('+'):
        mod = int(word.strip('+'))
    elif word.startswith('-'):
        mod = int(word)
    else:
        mod = ''
    return mod


# Rolling 2d20 with Advantage/Disadvantage
def vantage(start):
    temp = start.split(' ', 1)

    if len(temp) > 1:
        mod = get_mod(strip_parts(temp[1]))
    else:
        temp.append('')
        mod = 0

    rolls = roll_dice(num=2)

    text = get_response() + grammer(rolls[0]) + str(rolls[0]) + ' and ' + str(
        rolls[1]) + ' ' + temp[1]

    if temp[0].startswith('adv'):
        text += "\nYou get to use " + str(max(rolls) + mod) + crit(max(rolls))
    else:
        text += "\nYou get to use " + str(min(rolls) + mod) + crit(min(rolls))

    return text


# Rolling a specific series of dice
def normal_dice(start):
    temp = start.split(' ', 1)

    if len(temp) == 1:
        mod = ''
        reroll = 0
    else:
        mod, reroll = map(str, check_reroll(temp[1]))

    dice = temp[0].split('d')
    if dice[0] == '':
        dice[0] = 1

    rolls = roll_dice(reroll=int(reroll), num=int(dice[0]), sides=int(dice[1]))

    return stringify_rolls(rolls, mod)


# Rolling d20s or percentile dice
def roll_20s(start):

    if start == '':
        mod = 0
        roll = roll_dice()
    elif start.startswith('perc'):
        temp = start.split(' ', 1)
        if len(temp) == 1:
            mod = 0
            start = ''
        else:
            start = strip_parts(temp[1])
            mod = get_mod(start)
        roll = roll_dice(sides=100)
    else:
        mod = get_mod(strip_parts(start))
        roll = roll_dice()
    total = roll + mod

    text = get_response() + grammer(roll) + str(roll)

    if mod == 0:
        text += start + crit(roll)
    else:
        text += strip_parts(start) + get_response("end") + str(total) + crit(
            roll)

    return text


# Roll 7 sets of 4d6, drop the lowest roll, and output to channel
def stat_block():
    stats = []

    for i in range(7):
        temp = roll_dice(sides=6, num=4)
        temp.remove(min(temp))
        stats.append(sum(temp))

    text = get_response('stats')
    for i in range(7):
        if i == 6:
            text += get_response('mulligans').format(str(stats[i]))
        elif i == 5:
            text += str(stats[i])
        else:
            text += str(stats[i]) + ', '

    return text


# Drink health potion
def drink_potions(start):
    potion = start.split(' ')[1]

    if potion.startswith('heal'):
        mod = num = 2
    elif potion.startswith('great'):
        mod = num = 4
    elif potion.startswith('super'):
        mod = num = 8
    elif potion.startswith('supre'):
        num = 10
        mod = 20
    else:
        return "I don't think I know that potion"

    hp = sum(roll_dice(4, num)) + mod
    return get_response('health').format(hp)


client = discord.Client()


# Starts up the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Main bot operations
@client.event
async def on_message(message):

    # Sanity check to keep the bot from responding to itself
    if message.author == client.user:
        return

    msg = message.content.lower()

    if msg == '$roll help':
        text = ''
        with open('help.txt') as f:
            for line in f:
                text += line
        await message.channel.send(text)

    elif msg.startswith('$roll'):
        secret = check_secret(msg)

        # Checks if a modifier/more commands are given
        if msg == "$roll":
            start = ''
        else:
            start = msg.split(' ', 1)[1]
            start = strip_parts(start, 'secret')

        # Just rolls a d20
        if start == '':
            text = roll_20s(start)

        # Roll a d20 with a modifier
        elif start.startswith('+') or start.startswith('-'):
            text = roll_20s(start)

        # Roll 2d20 with advantage with or without a modifier
        elif start.startswith('adv') or start.startswith('dis'):
            text = vantage(start)

        # Roll other specific device
        elif start[0].isdigit() or start[0] == 'd':
            text = normal_dice(start)

        # Roll percentile dice
        elif start.startswith('perc'):
            text = roll_20s(start)

        # Roll character stats
        elif start.startswith('stats'):
            text = stat_block()

        elif start.startswith('potion'):
            text = drink_potions(start)

        # Checks if the user wants to make the roll a secret or not
        if secret:
            await message.channel.send(get_response("secret"))
            await message.author.send(text)
        else:
            await message.channel.send(text)


# The run command for the bot
client.run(os.getenv('DISCORD_TOKEN'))
