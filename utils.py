import discord, random
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

    url = random.choice([
        'https://c.tenor.com/bEBxkuyFiucAAAAM/yes-nice.gif',
        'https://c.tenor.com/OKR75dXb7AIAAAAM/nice-south-park.gif',
        'https://c.tenor.com/S_wekPtfKm4AAAAM/nice-michael-scott.gif',
        'https://media2.giphy.com/media/LCdix2ZGzI2ty/200.gif'
    ])
    embed = discord.Embed(color=0xff0000)
    embed.set_image(url=url)
    return embed


def embed_maker(title, rolls, author, icon, quip='', gif=''):
    # if "&" not in rolls:
    #     rolls = ' '

    embed = discord.Embed(title=title+str(rolls[0]), 
                          # description=rolls[0], 
                          color=0xff0000)
    embed.set_author(name=author, icon_url=icon)
    if quip != '':
        embed.add_field(name=quip, value="~", inline=False)
    if gif != '':
        embed.set_image(url=gif)
    return embed
