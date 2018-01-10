import discord
import asyncio
import random
import math
from Player import Player
from Game import Game
from discord.ext import commands
from discord.ext.commands import Bot
channel = ""
playerlist = []
firstMessage = True
SecretHitlerBool = False


my_bot = Bot(command_prefix="!")

@my_bot.event
async def on_ready():
    print('Logged in as')
    print(my_bot.user.name)
    print(my_bot.user.id)
    print('Invite: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(my_bot.user.id))
    print('------')






@my_bot.command()
async def SecretHitler(*args):
    global SecretHitlerBool
    await my_bot.send_message(channel,"All players that want to play say 'Secret Hitler'")
    SecretHitlerBool = True

@my_bot.command()
async def play(*args):
    global playerlist
    SecretHitlerBool = False
    players = [Player(str(x)[:-5],x,my_bot) for x in playerlist]
    try:
        g = Game(players, my_bot, channel)
        await g.play()
    except:
        await my_bot.send_message(channel,"You don't have the correct amount of members you bozos. \nI'm gonna clear the list and if you want to play again, restart the game")
    playerlist = []





# 

@my_bot.event
async def on_message(message):
    global firstMessage, SecretHitlerBool
    # we do not want the bot to reply to itself
    if message.author == my_bot.user:
        return

    if message.content == "set channel" or firstMessage:
        global channel
        channel = message.channel
        await my_bot.send_message(channel, "This has now been set to my default channel")

    if message.content.lower()=='secret hitler' and SecretHitlerBool==True:
        global playerlist
        if message.author not in playerlist:
            await my_bot.send_message(channel, str(message.author)[:-5] + ' is playing Secret Hitler')
            playerlist.append(message.author)
        else:
            await my_bot.send_message(channel, 'You are already playing the game silly')

    firstMessage = False
    await my_bot.process_commands(message)

my_bot.run("MzE3ODM5MzY4NTcwMDExNjUz.DApqiA.za3sxT_y0wes3z46TDKI7elJkEU")
