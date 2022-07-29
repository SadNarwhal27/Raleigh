import json
from replit import db


# Manipulates the DB of responses if on the testing server
def db_change(command, key, text, guild, GUILD):
    keyed = True if key != None else False

    if guild.id == GUILD:
        if command == 'keys':
            response = list(db.keys())
        elif command == 'values' and keyed:
            response = db[key]
        elif command == 'delete' and keyed:
            temp = db[key]
            if text in temp:
                temp.remove(text)
                db[key] = temp
            response = 'Removed: {}'.format(text)
        elif command == 'add' and keyed:
            temp = db[key]
            temp.append(text)
            db[key] = temp
            response = 'Added: {}'.format(text)
        else:
            response = 'No valid command detected. Please try again.'
    else:
        response = 'You do not have permission to do that.'

    return response


# Fills the DB with data from a JSON file if on the testing server
def db_fill(guild, GUILD):
    if guild.id == GUILD:
        response = 'Filling DB'
        with open('responses.json') as f:
            temp = json.load(f)

        for key in temp.keys():
            db[key] = temp[key]
    else:
        response = 'You do not have permission to do that.'

    return response
