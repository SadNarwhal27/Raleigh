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


# Returns a or an depending on the number rolled for grammer's sake
def grammer(total):
    checks = [8, 11, 18, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
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
    text = get_response() + ' '
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

    if character_limiter(text):
        text = get_response("end") + str(total)
    else:
        text += get_response("end") + str(total)

    return text + nice(total)


# Rolls dice from inputs
def roll_dice(sides=20, num=1):
    if sides == 0 or num == 0:
        roll = 0
    elif num == 1:
        roll = random.randint(1, sides)
    else:
        roll = []
        for i in range(num):
            roll.append(random.randint(1, sides))
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
        temp.append('')

    dice = temp[0].split('d')
    rolls = roll_dice(num=int(dice[0]), sides=int(dice[1]))

    return stringify_rolls(rolls, temp[1])


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
        text += strip_parts(start) + get_response("end") + str(total) + crit(roll)

    return text


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
        elif start[0].isdigit():
            text = normal_dice(start)

        # Roll percentile dice
        elif start.startswith('perc'):
            text = roll_20s(start)

        # Checks if the user wants to make the roll a secret or not
        if secret:
            await message.channel.send(get_response("secret"))
            await message.author.send(text)
        else:
            await message.channel.send(text)


# The run command for the bot
client.run(os.getenv('TOKEN'))
