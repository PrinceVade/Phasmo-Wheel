# Hunter Graves
# 25/06/2022
# phasmo-wheel.py

# A randomizer for Phasmophobia.
# From a collection of files ./traits and ./items it assigns one trait and one item.
# There is also a bonus wheel when 3/4 objectives are achieved that can be spun to increase fun.

# Discord.py imports
import discord
from discord.ext import commands,tasks
from discord.ext.commands import CommandNotFound

# Python libraries
import random
from os import listdir
from Levenshtein import distance

# The token and description of the bot.
DEBUG = False
TOKEN = 'OTkwMzAxODQ5OTQ3MDc4Njg2.Gf8sYH.S1Gj0vMekMYovUhVZdJTc0okpfM3hmQkrt0e_w'
description = '''I am configured to randomly assign traits and banned items when asked.
Make sure to read the !rules and use !help when needed. Good luck!'''

# defining the bot's command prefix as well as adding the description.
bot = commands.Bot(command_prefix='!', description=description, case_insensitive=True)

def getTrait(traitList):
    conflictItems = []
    selectedTrait = random.choice(traitList)
    if DEBUG:
        print(selectedTrait)
    
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

def getRandomFromList(ListOfChoices):
    chosen = random.choice(ListOfChoices)
    return chosen.replace('.txt', '')

def findClosestCommand(given):
    commands = ['spin', 'trait', 'item', 'bonus', 'punish', 'rules', 'map', 'diff', 'howhard', 'monika', 'newgame', 'start', 'fresh']
    closest = commands[0]
    closestDistance = distance(given, closest)
    
    for c in commands[1:]:
        cLen = distance(given, c)
    
        if cLen < closestDistance:
            closest = c
            closestDistance = cLen

    return closest

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

@bot.command(name = 'item',
    description = 'Spins the item wheel, excluding any conflict items from the given trait')
async def item(ctx, traitName = ''):
    conflicts = []
    if traitName:
        conflicts = getTrait([traitName + '.txt'])['conflicts']
    
    items = listdir('./items')
    await printItems([getItem(items, conflicts)], ctx)

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

@bot.command(name = 'map',
    description = 'Randomly chooses and prints a map choice.')
async def map(ctx):
    await ctx.send('Ghost detected at ' + getRandomFromList(listdir('./maps')))

@bot.command(name = 'diff',
    description = 'Randomly chooses and prints a difficulty choice.',
    aliases = ['difficulty', 'howhard', 'monika'])
async def diff(ctx):
    await ctx.send('Danger levels reading at ' + getRandomFromList(listdir('./difficulties')))

@bot.command(name = 'newgame',
    description = 'Sets up a new game and prints a map and difficulty.',
    aliases = ['fresh', 'start'])
async def newgame(ctx):
    await ctx.send('```Ghost detected at ' + getRandomFromList(listdir('./maps')) + '\nDanger levels reading at ' + getRandomFromList(listdir('./difficulties')) + '```')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print(error)
        
        textOptions = [
            "*sigh* Zack, let's stick to commands that actually exist, shall we?",
            "Oops, you probably pulled a Zack!",
            "3Drunk5Phasmo. Try again, pl0x.",
            "Error 404, " + ctx.message.content[1:] + " not Found. ",
            "Zachariah Wayne Dreitzler, you get your act together this instant!",
            "Is Bames Nond having a stronk?",
            "The Zack is strong with this one...",
            "01100100 01110101 01101101 01100010 01100001 01110011 01110011",
            "Chaos is your friend, it seems. I'm just assuming you're doing this on purpose.",
            "*facepalm*",
            "I think I know what you mean:",
            "I'm too tried for this shit."
        ]
        
        await ctx.send(getRandomFromList(textOptions) + "\nYou were trying to run " + findClosestCommand(ctx.message.content[1:].lower()) + " right?")

bot.run(TOKEN)