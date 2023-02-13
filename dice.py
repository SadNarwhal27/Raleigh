import math, random
from simpleeval import simple_eval


# Determine the number of dice, their sides, and if vantage is called
def get_dice(setup):
    setup = setup.lower() if setup != None else ''

    if setup == None:
        dice, sides = 1, 20
    elif 'd' in setup:
        temp = (setup).split('d')
        dice = int(temp[0])
        sides = int(temp[1])
    elif 'per' in setup:
        dice, sides = 1, 100
    else:
        dice, sides = 1, 20

    return dice, sides


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
