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


# Checks if a $roll command gets a crit
def check_nats(rolls):
    if max(rolls) == 20:
        response = get_response('nat20')
    elif max(rolls) == 1:
        response = get_response('nat1')
    else:
        response = ''
    return response