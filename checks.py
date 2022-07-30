import random
from replit import db


# Grabs a response from a JSON file of responses
def get_response(category="start"):
    return random.choice(db[category])


# Checks the total for funny numbers
def check_nice(total):
    quips = db['nice']
    total = str(total)
    return quips[total] if total in quips.keys() else ''


# Checks if a Nat 20 or Nat 1
def get_vantage(content, rolls):
    if 'adv' in content.lower():
        focus = max(rolls)
    else:
        focus = min(rolls)
    response, gif = check_nats(focus)
    return response, gif, str(focus)


# Makes sure responses are less than 2000 characters for Discord
def check_size(text, total):
    if len(text) > 2000:
        response = get_response('end').format(total) + check_nice(total)
    else:
        response = text + get_response('end').format(total) + check_nice(total)
    return response


# Checks if a $roll command gets a crit
def check_nats(roll):
    url = ''
    if roll == 20:
        response = get_response('nat20')
        url = "https://i.gifer.com/1RUS.gif"
    elif roll == 1:
        response = get_response('nat1')
        url = 'https://media2.giphy.com/media/9NLYiOUxnKAJLIycEv/giphy.gif?cid=e1bb72ff5b7270964f754e4773367e12'
    else:
        response = ''
    return response.replace('\n', ''), url
