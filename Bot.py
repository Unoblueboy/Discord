import discord
import asyncio
import random
import math
from discord.ext.commands import Bot
my_bot = Bot(command_prefix="!")
channel = ""

@my_bot.event
async def on_ready():
    print("Client logged in")

@my_bot.command()
async def hello(*args):
    return await my_bot.say("Hello, world!")

@my_bot.command()
async def exit(*args):
    quit()




SecretHitlerBools = [False,False, False] # [Playing full game, Recruiting Players, Main Game Started]
playerlist=[]
hitler = ""
president = ""
fascists = []
chancellor = ""
deck = ["l"]*6 + ["f"]*11
discard = []
libpolicies = 0
faspolicies = 0
veto = [False,False] # Ability to veto, Vetoed this turn

@my_bot.command()
async def SecretHitler(*args):
    global SecretHitlerBools
    reset()
    await my_bot.send_message(channel,"All players that want to play say 'Secret Hitler'")
    SecretHitlerBools[0] = True
    SecretHitlerBools[1] = True

@my_bot.command()
async def r():
    reset()

def reset():
    global playerlist, SecretHitlerBools, hitler, fascists, president, chancellor
    global deck, discard, libpolicies, faspolicies, veto
    SecretHitlerBools = [False,False, False]
    playerlist=[]
    hitler = ""
    president = ""
    fascists = []
    chancellor = ""
    deck = ["l"]*6 + ["f"]*11
    discard = []
    libpolicies = 0
    faspolicies = 0
    veto = [False,False]

@my_bot.command()
async def Start(*args):
    if SecretHitlerBools[0] == True and SecretHitlerBools[1] == True:
        noOfPlayers = 10 #len(playerlist)
        if noOfPlayers < 5:
            reset()
            await my_bot.send_message(channel,"You don't have enough players to play")
        else:
            global hitler, fascists, playerlist, deck, discard, libpolicies, faspolicies, veto, president, chancellor
            random.shuffle(deck)
            SecretHitlerBools[2] = True
            # fascists = random.sample(playerlist,math.ceil((noOfPlayers-4)/2))
            fascists = random.sample(playerlist,1)
            hitler = fascists[0]
            choice = [False, False]
            curPres = ""
            while hitler in fascists:
                hitler = random.sample(playerlist,math.ceil(1))[0]
            for user in playerlist:
                if user != hitler and user not in fascists:
                    await my_bot.send_message(user,content="You are a liberal")
                elif user in fascists:
                    await my_bot.send_message(user,content="You are a fascist")
                    await my_bot.send_message(user,content="All the fascists are:")
                    for fascist in fascists:
                        await my_bot.send_message(user,content=str(fascist)[:-5])
                    await my_bot.send_message(user,content="Hitler is")
                    await my_bot.send_message(user,content=str(hitler)[:-5])
                else:
                    await my_bot.send_message(user,content="You are a Hitler")
                    if noOfPlayers<=6:
                        await my_bot.send_message(user,content="All the fascists are:")
                        for fascist in fascists:
                            await my_bot.send_message(user,content=str(fascist)[:-5])
            while True:
                if choice[0]:
                    curPres = president
                    await select_president(True)
                    choice[1]=True
                else:
                    await select_president()
                yes, no = await vote()
                while len(yes) <= len(no):
                    await my_bot.send_message(channel, ", ".join(yes) + " voted ja, and " + ", ".join(no) + " voted nein.")
                    await select_president()
                    yes, no = await vote()
                await my_bot.send_message(channel, ", ".join(yes) + " voted ja, and " + ", ".join(no) + " voted nein.")
                if faspolicies >=3:
                    if chancellor == hitler:
                        await my_bot.send_message(channel, "The fascists have won")
                        break
                    else:
                        await my_bot.send_message(channel, str(chancellor)[:-5] + " is not hitler")
                await president_cards()
                if deck[0] == "l":
                    libpolicies+=1
                    await my_bot.send_message(channel, "A liberal policiy was played")
                    await my_bot.send_message(channel, "liberal policies: " + str(libpolicies))
                    await my_bot.send_message(channel, "fascist policies: " + str(faspolicies))
                    if libpolicies == 5:
                        await my_bot.send_message(channel, "The liberals have won")
                        break
                else:
                    faspolicies+=1
                    await my_bot.send_message(channel, "A liberal policiy was played")
                    await my_bot.send_message(channel, "liberal policies: " + str(libpolicies))
                    await my_bot.send_message(channel, "fascist policies: " + str(faspolicies))
                    if noOfPlayers <= 6:
                        # 3 is peak top 3 cards
                        if faspolicies == 3:
                            await my_bot.send_message(president, "These are the top three cards of the deck:")
                            for card in deck[:3]:
                                if card == "l":
                                    await my_bot.send_message(president, "Liberal")
                                else:
                                    await my_bot.send_message(president, "Fascist")
                        # 4 is kill
                        if faspolicies == 4:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 5 is kill + veto unlocked
                        if faspolicies == 5:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            veto[0]=True
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 6 is win
                        if faspolicies == 6:
                            await my_bot.send_message(channel, "The fascists have won")
                            break
                    elif noOfPlayers <= 8:
                        pass
                        # 2 is investigate player identity
                        if faspolicies == 2:
                            await my_bot.send_message(president, "Please choose someone to inspect")
                            await my_bot.send_message(channel, "The president is choosing who to inspect")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        inspected = playerlist[indice]
                                    if inspected not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif inspected == president:
                                        await my_bot.send_message(president, "You can't inspect yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to inspected " + str(inspected)[:-5])
                                        if inspected == hitler or inspected in fascists:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a fascist")
                                        else:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a liberal")
                                        break
                                except:
                                    pass
                        # 3 is pick next president
                        choice = [True,False]
                        # 4 is kill
                        if faspolicies == 4:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 5 is kill + veto unlocked
                        if faspolicies == 5:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            veto[0]=True
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 6 is win
                        if faspolicies == 6:
                            await my_bot.send_message(channel, "The fascists have won")
                            break
                    else:
                        pass
                        # 1 is investigate player identity
                        if faspolicies == 1:
                            await my_bot.send_message(president, "Please choose someone to inspect")
                            await my_bot.send_message(channel, "The president is choosing who to inspect")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        inspected = playerlist[indice]
                                    if inspected not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif inspected == president:
                                        await my_bot.send_message(president, "You can't inspect yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to inspected " + str(inspected)[:-5])
                                        if inspected == hitler or inspected in fascists:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a fascist")
                                        else:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a liberal")
                                        break
                                except:
                                    pass
                        # 2 is investigate player identity
                        if faspolicies == 2:
                            await my_bot.send_message(president, "Please choose someone to inspect")
                            await my_bot.send_message(channel, "The president is choosing who to inspect")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        inspected = playerlist[indice]
                                    if inspected not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif inspected == president:
                                        await my_bot.send_message(president, "You can't inspect yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to inspected " + str(inspected)[:-5])
                                        if inspected == hitler or inspected in fascists:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a fascist")
                                        else:
                                            await my_bot.send_message(president, str(inspected)[:-5] + " is a liberal")
                                        break
                                except:
                                    pass
                        # 3 is pick next president
                        if faspolicies == 3:
                            choice = [True,False]
                        # 4 is kill
                        if faspolicies == 4:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 5 is kill + veto unlocked
                        if faspolicies == 5:
                            await my_bot.send_message(president, "Please choose someone to kill")
                            await my_bot.send_message(channel, "The president is choosing who to kill")
                            while True:
                                try:
                                    msg = await my_bot.wait_for_message(author=president)
                                    if msg.content in [str(x)[:-5] for x in playerlist]:
                                        indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                                        killed = playerlist[indice]
                                    if killed not in playerlist:
                                        await my_bot.send_message(president, "Please enter a valid user")
                                    elif killed == president:
                                        await my_bot.send_message(president, "You can't kill yourself silly")
                                    else:
                                        await my_bot.send_message(channel, "The president has decided to kill " + str(killed)[:-5])
                                        del playerlist[playerlist.index(killed)]
                                        break
                                except:
                                    pass
                            veto[0]=True
                            if killed == hitler:
                                await my_bot.send_message(channel, "The liberals have won")
                                break
                        # 6 is win
                        if faspolicies == 6:
                            win = True
                            await my_bot.send_message(channel, "The fascists have won")
                del deck[0]
                if len(deck)<3:
                    deck = random.shuffle(deck+discard)
                    discard = []
                if choice == [True,True]:
                    choice = [False,False]
                    president = curPres
                    curPres = ""








async def select_president(choice=False):
    global president, playerlist
    if not choice:
        if president == "":
            president = random.sample(playerlist,1)[0]
        else:
            president = playerlist[(playerlist.index(president)+1) % len(playerlist)]
    else:
        await my_bot.send_message(president, "Please choose the next president")
        await my_bot.send_message(channel, "The president is choosing the next president")
        while True:
            try:
                msg = await my_bot.wait_for_message(timeout=60.0, author=president)
                if msg.content in [str(x)[:-5] for x in playerlist]:
                    indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                    newpres = playerlist[indice]
                if newpres not in playerlist:
                    await my_bot.send_message(president, "Please enter a valid user")
                elif newpres == president:
                    await my_bot.send_message(president, "You cannot be president twice in a row silly")
                else:
                    president = newpres
                    break
            except:
                pass
        await my_bot.send_message(channel, str(president)[:-5] + " has elected " + str(chancellor)[:-5] + " as chancellor")
    await my_bot.send_message(channel, str(president)[:-5] + " is the current president")
    await my_bot.send_message(president, "Please enter the user name of the chancelor you would like to pick")
    await select_chancellor()

async def select_chancellor():
    global chancellor, playerlist, president
    while True:
        try:
            msg = await my_bot.wait_for_message(timeout=60.0, author=president)
            if msg.content in [str(x)[:-5] for x in playerlist]:
                indice = [str(x)[:-5] for x in playerlist].index(msg.content)
                chancellor = playerlist[indice]
            if chancellor not in playerlist:
                await my_bot.send_message(president, "Please enter a valid user")
            elif chancellor == president:
                await my_bot.send_message(president, "You cannot be president and chancellor silly")
            else:
                break
        except:
            pass
    await my_bot.send_message(channel, str(president)[:-5] + " has elected " + str(chancellor)[:-5] + " as chancellor")

async def vote():
    global playerlist
    yes = []
    no = []
    for player in playerlist:
        msg = await get_vote(player)
        if msg == "y":
            yes.append(str(player)[:-5])
        else:
            no.append(str(player)[:-5])
        # print(msg)
    return yes, no

async def get_vote(player):
    await my_bot.send_message(player, "Do you approve of this government, y/n?")
    msg = await my_bot.wait_for_message(author=player)
    try:
        msg = msg.content.lower()
    except:
        pass
    while msg not in ["y","n"]:
        my_bot.send_message(player, "Please enter valid data")
        msg = await my_bot.wait_for_message(author=player)
        try:
            msg = msg.content.lower()
        except:
            pass
    return msg

async def president_cards():
    global deck, discard, president, libpolicies, faspolicies
    cards = deck[:3]
    await my_bot.send_message(president, "These are the cards you can choose from: ")
    for card in cards:
        if card == "l":
            await my_bot.send_message(president, "Liberal")
        else:
            await my_bot.send_message(president, "Fascist")
    await my_bot.send_message(president, "Which card do you want to discard (l for liberal, f for fascist)")
    while True:
        discarded = await my_bot.wait_for_message(timeout=60.0,author=president)
        try:
            discarded=discarded.content.lower()
        except:
            pass
        if discarded in cards:
            break
        else:
            await my_bot.send_message(president, "Please choose a valid card Mr president")
    discard.append(discarded)
    del deck[deck.index(discarded)]
    await chancellor_cards()

async def chancellor_cards():
    global deck, discard, president, libpolicies, faspolicies
    cards = deck[:2]
    await my_bot.send_message(chancellor, "These are the cards you can choose from: ")
    for card in cards:
        if card == "l":
            await my_bot.send_message(chancellor, "Liberal")
        else:
            await my_bot.send_message(chancellor, "Fascist")
    await my_bot.send_message(chancellor, "Which card do you want to discard (l for liberal, f for fascist)")
    while True:
        discarded = await my_bot.wait_for_message(timeout=60.0,author=chancellor)
        try:
            discarded=discarded.content.lower()
        except:
            pass
        if discarded in cards:
            break
        else:
            await my_bot.send_message(chancellor, "Please choose a valid card Mr chancellor")
    discard.append(discarded)
    del deck[deck.index(discarded)]

@my_bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == my_bot.user:
        return

    if message.content.lower()=='set channel':
        global channel
        channel = message.channel
        await my_bot.send_message(channel, "This has now been set to my default channel")


    if message.content.lower()=='secret hitler' and SecretHitlerBools[1]==True:
        global playerlist
        if message.author not in playerlist:
            await my_bot.send_message(channel, str(message.author)[:-5] + ' is playing Secret Hitler')
            playerlist.append(message.author)
        else:
            await my_bot.send_message(channel, 'You are already playing the game silly')

    await my_bot.process_commands(message)

my_bot.run("MzE3MDUwNjUwMjgwMDY3MDcz.DAeL-Q.oa6XVpXR_rjvSUnXUl6KT1K2BwQ")
