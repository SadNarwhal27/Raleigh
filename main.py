import discord
import os
import random


# Rolls a set of dice and returns a list of rolls
def roll_dice(dice):

    # If someone inputs a d20 type string
    if dice[0] == '':
        num = 1
        sides = int(dice[1])

    elif dice[0] == '0' or dice[1] == '0':
        return [0]

    # Normal setup
    else:
        num = int(dice[0])
        sides = int(dice[1])

    rolls = []

    for i in range(num):
        rolls.append(random.randint(1, sides))

    return rolls


# Get the modifier
def get_mod(mod):
    mod = list(mod)

    if ' ' in mod:
        mod.remove(' ')

    if len(mod) >= 3:
        for i in range(2, len(mod)):
            mod[1] += mod[i]

    if mod[0] == '+':
        return int(mod[1])
    else:
        return -int(mod[1])


# Return the modifier as a string
def get_mod_text(mod):
    if (mod != ''):
        return '\nModifier: ' + mod.replace(' ', '')
    else:
        return ''


# Return a string of rolls
def get_rolls_text(rolls):
    dice_text = 'Dice Rolls: '

    for i in range(len(rolls)):
        if i == len(rolls) - 1:
            dice_text += ' ' + str(rolls[i])
        else:
            dice_text += ' {},'.format(rolls[i])

    return dice_text


# Return the sum total
def get_total_text(rolls, n):
    total = sum(rolls) + n
    return '\nTotal: ' + str(total) + nice(total)


# Checks if the total has a funny outcome
def nice(num):
    if num == 69:
        output = '\nNice!'
    elif num == 6969:
        output = '\nSuper Nice!'
    elif num == 420:
        output = '\nBlaze It!'
    else:
        output = ''

    return output


def crit(start, rolls):
    temp = start.split(' ')[0]

    if temp == '1d20' or temp == '2d20':
        if 20 in rolls:
            return "\nThat's a crit!"
        elif 1 in rolls:
            return "\nThat's a crit fail!"
        else:
            return ''

    else:
        return ''


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

    # Test message to make sure things are working
    if msg.startswith('$hello'):
        await message.channel.send('Hello!')

    # Outputs rolls
    if msg.startswith('$rol'):
        start = msg.split(' ', 1)[1]

        # Checks if percentile is called
        if 'perc' in start:
            roll = random.randint(1, 100)

            mod = ''
            if ' ' in start:
                temp = start.split(' ', 1)
                mod = temp[1]

                n = 0
                if mod != '':
                    n = get_mod(mod)

                text = 'Percentile: ' + str(roll) + get_mod_text(
                    mod) + get_total_text([roll], n)

            else:
                text = 'Percentile: ' + str(roll) + nice(roll)

        # Help command
        elif start == 'help':
            text = 'My name is Raleigh, the dice rolling robot!\nCommands: \nGet some Help - $roll help\nRoll Dice - $roll 4d6\nRoll Dice with a Modifier - $roll 4d6 +3\nRoll Percentile Dice - $roll percentile\nRoll Percentiles with a Modifier - $roll percentile +5'

        # Sanity check if someone puts in too many dice at once
        elif int(start.split('d', 1)[0]) > 500:
            text = "That's too many dice for me to roll. I can only roll a max of 500"

        # Rolling normal dice
        else:
            mod = ''
            if ' ' in start:
                temp = start.split(' ', 1)
                mod = temp[1]
                rolls = roll_dice(temp[0].split('d', 1))
            else:
                rolls = roll_dice(start.split('d', 1))

            n = 0
            if mod != '':
                n = get_mod(mod)

            text = get_rolls_text(rolls) + get_mod_text(mod) + get_total_text(
                rolls, n) + crit(start, rolls)

        await message.channel.send(text)


client.run(os.getenv('TOKEN'))
