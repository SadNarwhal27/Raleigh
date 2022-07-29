import random
from simpleeval import simple_eval


# Displays an embedded help doc for users
def get_help():
    text = ''
    with open('help.txt') as f:
        for line in f:
            text += line
    return text


def get_flip():
    response = random.choice(['Heads', 'Tails'])
    return response

# Does math using a safer eval message
def get_math(message):
    response = simple_eval(message)
    return response

def six_nine():
    response = random.choice(['Nice 👌', 'Noice 😎', 'Niiiiiice ♋'])
    return response