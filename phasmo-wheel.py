# Hunter Graves
# 25/06/2022
# phasmo-wheel.py

# A randomizer for Phasmophobia.
# From a collection of files ./traits and ./items it assigns one trait and one item.
# There is also a bonus wheel when 3/4 objectives are achieved that can be spun to increase fun.

# Discord.py imports
import discord
from discord.ext import commands,tasks

# Python libraries
import random
from os import listdir

# The token and description of the bot.
DEBUG = False
TOKEN = ''
description = '''I am configured to randomly assign traits and banned items when asked.
I respond to the commands !spin, !trait, !punish and !bonus. Good luck!'''

# defining the bot's command prefix as well as adding the description.
bot = commands.Bot(command_prefix='!', description=description)

def getTrait(traitList):
    conflictItems = []
    selectedTrait = random.choice(traitList)
    
    with open('./traits/' + selectedTrait, 'r') as file:
        traitText = [l.strip() for l in file.readlines()]
        
        # Now that we have all the information, get the list of Items that cant be banned
        # then remove that info from the text for printing
        conflictItems = traitText[traitText.index('Conflict Items:')+1:]
        traitText = traitText[:traitText.index('Conflict Items:')]

    return {'trait': selectedTrait.replace('.txt', ''), 'text': traitText, 'conflicts': conflictItems}

def getItem(itemList, conflictList):
    items = [i for i in itemList if i not in conflictList]
    return random.choice(items)

def checkAddTraits(traitDict):
    # do nothing for now, still braintstorm wtf to do here
    return false

def checkAddItems(itemList, traitDict):
    bannedItems = []
    if traitDict['trait'] == 'Forgetful':
        # spin two more banned items
        bannedItems += [getItem(itemList, traitDict['conflicts'])]
        bannedItems += [getItem(itemList, traitDict['conflicts'])]
    
    return bannedItems

def getBonus(folderName):
    bonusList = listdir('./' + folderName)
    bonus = random.choice(bonusList)
    
    with open('./' + folderName + '/' + bonus, 'r') as file:
        bonusText = [l.strip() for l in file.readlines()]

    return {'name': bonus.replace('.txt', ''), 'text': '\n'.join(bonusText)}

async def printTrait(traitDict, ctx):
    await ctx.send('```' + traitDict['trait'] + ':\n' + '\n'.join(traitDict['text']) +'```')

async def printItems(itemNames, ctx):
    output = ''
    if len(itemNames) > 1:
        output = ', '.join(itemNames)
    else:
        output = itemNames[0]

    await ctx.send('```Banned Item:\n' + output + '```')

@bot.command(name = 'spin',
    description = 'Spin the Phasmo-Wheel')
async def spin(ctx):
    # set lists for the get commands
    traits = listdir('./traits')
    items = listdir('./items')

    # builds a dict with trait, text, and conflicts
    traitDict = getTrait(traits)

    # First, print the trait before we do anything else
    await printTrait(traitDict, ctx)
    
    # Check if the trait means we need to print any extra stuff
    # First, check for extra traits, because that will expand the list of conflict items.
    if traitDict['text'] == 'Liar':
        extraTrait = getTrait()
        traitDict['conflicts'] += extraTrait('conflicts')
        await printTrait(extraTrait, ctx)

    bannedItems = [getItem(items, traitDict['conflicts'])]
    bannedItems += checkAddItems(items, traitDict)
    
    await printItems(bannedItems, ctx)

@bot.command(name = 'trait',
    description = 'Spin the trait wheel')
async def trait(ctx):
    traits = listdir('./traits')
    traitDict = getTrait(traits)
    await printTrait(traitDict, ctx)

@bot.command(name = 'bonus',
    description = 'Spin the bonus wheel!')
async def bonus(ctx):
    bonusDict = getBonus('bonuses')
    await ctx.send('```' + bonusDict['name'] + ':\n' + bonusDict['text'] + '```')
    
@bot.command(name = 'punish',
    description = 'Spin the punishment wheel')
async def punish(ctx):
    punishDict = getBonus('punishments')
    await ctx.send('```' + punishDict['name'] + ':\n' + punishDict['text'] + '```')

@bot.command(name = 'rules',
    description = 'Print the rules')
async def rules(ctx):
    with open('Rules.txt', 'r') as file:
        text = [l.strip() for l in file.readlines()]

    await ctx.send('```Rules:\n' + '\n'.join(text) + '```')

@bot.command(name = 'give',
    description = 'debug command. Prints exact trait(+random item(s)) provided')
async def give(ctx, trait: str):
    if DEBUG:
        traitDict = getTrait([trait + '.txt'])
        items = listdir('./items')
        
        await printTrait(traitDict, ctx)
        
        bannedItems = [getItem(items, traitDict['conflicts'])]
        bannedItems += checkAddItems(items, traitDict)
        
        await printItems(bannedItems, ctx)
    

bot.run(TOKEN)