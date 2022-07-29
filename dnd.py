from dice import roll_dice
from checks import get_response

def make_character():
    stats = []

    for _ in range(6):
        rolls = roll_dice(4, 6)
        rolls.remove(min(rolls))
        stats.append(sum(rolls))

    text = get_response('stats')
    text += ', '.join(list(map(str, stats)))

    mulligan = roll_dice(4, 6)
    mulligan.remove(min(mulligan))

    text += get_response('mulligans').format(sum(mulligan))

    return text

def drink_potion(drink):
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

    return response