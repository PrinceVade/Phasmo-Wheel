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
import logging
import random
from os import listdir
from Levenshtein import distance
from datetime import datetime as dt

# The token and description of the bot.
DEBUG = False
TOKEN = 'OTkwMzAxODQ5OTQ3MDc4Njg2.G7CheH.tyECHNqEtfaSKMiZy9vr-2iy4whtbtpaR6AetA'
description = '''I am the Phasmo-Bot! Designed to make Phasmophobia a more terrible and amazing experience!
It is optimal to use this bot once your party has either achieved level 30 or is considered profient at hunting ghosts.
You can play otherwise, but there will be quite a lot of !punish going on.

To use, you should have a channel dedicated to Phasmophobia where everyone playing can see messages.
There, use the !newgame command in order to print a random map, gamemode, and difficulty.
If you are unfamiliar with the gamemode presented, use the "!rules <gamemode>" commands to print the rules.
If you find a bug, use the "!bug" command to get the link to submit issues.
Follow the instructions and have fun. Good luck!'''

# quick log configuration
logLevel = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(filename='./logs/' + dt.now().strftime('%m%d%Y-%H%M') + '.log', encoding='utf-8', level=logLevel)
    
# a global variable to help track election status
activeElection = False
activeElectionFraud = False
activeElectionVotesNeeded = 0
votes = {}

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
    return False

def checkAddItems(itemList, traitDict, alreadyBanned = []):
    bannedItems = []
    if traitDict['trait'] == 'Forgetful':
        # spin two more banned items
        bannedItems += [getItem(itemList, alreadyBanned + bannedItems)]
        bannedItems += [getItem(itemList, alreadyBanned + bannedItems)]
    
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
    bannedItems += checkAddItems(items, traitDict, bannedItems)
    
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
    description = 'Spin the bonus wheel!',
    aliases = ['good', 'reward'])
async def bonus(ctx):
    bonusDict = getBonus('bonuses')
    await ctx.send('```' + bonusDict['name'] + ':\n' + bonusDict['text'] + '```')
    
@bot.command(name = 'punish',
    description = 'Spin the punishment wheel',
    aliases = ['punishment', 'bad'])
async def punish(ctx):
    punishDict = getBonus('punishments')
    await ctx.send('```' + punishDict['name'] + ':\n' + punishDict['text'] + '```')

@bot.command(name = 'give',
    description = 'debug command. Prints exact trait(+random item(s)) provided')
async def give(ctx, trait: str):
    if DEBUG:
        traitDict = getTrait([trait + '.txt'])
        logging.debug(traitDict)
        print(traitDict)
        
        items = listdir('./items')
        
        await printTrait(traitDict, ctx)
        
        bannedItems = [getItem(items, traitDict['conflicts'])]
        bannedItems += checkAddItems(items, traitDict, bannedItems)
        logging.debug(bannedItems)
        print(bannedItems)
        
        await printItems(bannedItems, ctx)

@bot.command(name = 'list',
    description = 'Lists all of the items specified in the command (should be plural)')
async def printList(ctx, query: str):
    try:
        dirList = listdir('./' + query.lower())
        trimmedList = [i.replace('.txt', '') for i in dirList]
        print(trimmedList)
        await ctx.send("Found a total of " + str(len(trimmedList)) + " " + query + ":```\n" + '\n'.join(trimmedList) + "```\nYou can find all details here `https://github.com/PrinceVade/Phasmo-Wheel`")
    except:
        await ctx.send("Couldn't find anything called " + query + ". Try again (make sure it's plural) or contact the dev.")

@bot.command(name = 'map',
    description = 'Randomly chooses and prints a map choice.')
async def map(ctx):
    await ctx.send('Ghost detected at ' + getRandomFromList(listdir('./maps')))

@bot.command(name = 'diff',
    description = 'Randomly chooses and prints a difficulty choice.',
    aliases = ['difficulty', 'howhard', 'monika'])
async def diff(ctx):
    await ctx.send('Danger levels reading at ' + getRandomFromList(listdir('./difficulties')))

@bot.command(name = 'mode',
    description = 'Randomly chooses and prints a game mode to play.',
    aliases = ['gamemode'])
async def gamemode(ctx):
    await ctx.send('Gamemode adjusted to ' + getRandomFromList(listdir('./modes')))

@bot.command(name = 'newgame',
    description = 'Sets up a new game and prints a map and difficulty.',
    aliases = ['fresh', 'start', 'new'])
async def newgame(ctx):
    await ctx.send('```Ghost detected at ' + getRandomFromList(listdir('./maps')) + '\nDanger levels reading at ' + getRandomFromList(listdir('./difficulties')) + '```') #\nGamemode adjusted to ' + getRandomFromList(listdir('./modes')) + '```')

@bot.command(name = 'vote',
    description = 'Cast a vote in the currently running election.')
async def vote(ctx, ballot: str):
    global activeElection
    global votes
    global activeElectionFraud
    global activeElectionVotesNeeded
    
    if activeElection:
        if (len(votes) >= activeElectionVotesNeeded):
            # vote is invalid, election is over.
            await ctx.send("Oop! Election is already over. Please use !election to see the results.")
        elif (str(ctx.message.author.id) in votes.keys()) and (not activeElectionFraud):
            logging.info('Duplicate vote cast by ' + str(ctx.message.author.name) + '. Vote was: ' + ballot)
            await ctx.send("You've already voted: No committing voter fraud! Silly goose.")
        else:
            logging.info('Vote in election cast by ' + str(ctx.message.author.name) + '. Vote was: ' + ballot)
            votes[str(ctx.message.author.id)] = ballot.lower()
            await ctx.send('Thank you for your vote!')
    else:
        await ctx.send('There is no active election, please run !election before voting.')

@bot.command(name = 'election',
    description = 'Begins the election process.',
    aliases = ['mvp', 'lvp'])
async def election(ctx, nominees = '4', fraud = False):
    global activeElection
    global votes
    global activeElectionFraud
    global activeElectionVotesNeeded
    
    if activeElection:
        if (len(votes) >= activeElectionVotesNeeded) or (nominees.lower() == 'cancel'):
            # this means that the election is over.
            logging.info('Election finished. Logging results: ' + str(votes))
            
            activeElection = False
            peopleThatMatter = set(votes.values())
            results = {p: list(votes.values()).count(p) for p in peopleThatMatter}
            
            formattedResults = "```"
            for person in results.keys():
                formattedResults += person + ': ' + str(results[person]) + '\n'

            await ctx.send('Election results:' + formattedResults + '```')
        else:
            logging.info("Additional election command run. Value of: (len(votes) >= activeElectionVotesNeeded) or (nominees.lower() == 'cancel')\n`(len(" + str(votes) + ") >= " + str(activeElectionVotesNeeded) + ") or (" + nominees + ".lower() == 'cancel')`")
            await ctx.send("There's already an active election in progress. Currently " + str(len(votes)) + "/" + str(activeElectionVotesNeeded) + " votes cast.")
    else:
        logging.info('Election begun. ' + nominees + ' needed to complete.')
        activeElection = True
        votes = {}
        activeElectionFraud = fraud
        activeElectionVotesNeeded = int(nominees)
        await ctx.send("A new election has begun! Cast votes via DM.")

@bot.command(name = 'bug',
    description = 'Prints the link to submit bugs.')
async def bug(ctx):
    await ctx.send('`https://github.com/PrinceVade/Phasmo-Wheel/issues`')

@bot.command(name = 'rules',
    description = 'Print the rules for a given gamemode.')
async def rules(ctx, mode: str):
    try:
        with open('./modes/' + mode  + '.txt', 'r') as file:
            modeRules = [l.strip() for l in file.readlines()]
    
        await ctx.send('```' + mode +  ' Rules:\n' + '\n'.join(modeRules) + '```')
    except:
        await ctx.send('I could not find a mode called ' + mode + '. Check the spelling with "!list modes". Or contact your admin.')

@bot.event
async def on_command(ctx):
    logging.info(ctx.command.name + ' called with arguments ' + str(ctx.kwargs))

@bot.event
async def on_command_completion(ctx):
    suffix = 'successfully.'
    if ctx.command_failed:
        suffix = 'unsuccessfully.'

    logging.info(ctx.command.name + ' completed ' + suffix)

@bot.event
async def on_command_error(ctx, error):
    logging.error('CommandError detected: ' + str(error))

    if isinstance(error, CommandNotFound):
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
            "I'm too tried for this shit.",
            "Derek!"
        ]
        
        await ctx.send(getRandomFromList(textOptions) + "\nYou were trying to run " + findClosestCommand(ctx.message.content[1:].lower()) + " right?")

bot.run(TOKEN)