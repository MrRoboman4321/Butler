import traceback
import datetime
import discord
import asyncio
import random
import pickle
import sys
import os
import re

from os import path
from discord.ext import commands

settings = {}
servers = []
users = {}

bot = commands.Bot(command_prefix='!', description="I am a bot, beep boop")

def saveSettings(settings, server):
    pickle.dump(settings[server], open('./settings/servers/' + str(server) + '.svr', 'wb'))

def saveUsers(users, user):
    pickle.dump(users[user], open('./settings/users/' + str(user) + '.usr', 'wb'))

def isAuthed(message, settings, server):
    if message.author.name == "Ronoman":
        return True
    for i in settings[server]['authedRoles']:
        for j in message.author.roles:
            if i == j.name:
                return True
    return False

def format_ts():
    return "[please clap]"

@bot.event
@asyncio.coroutine
def on_ready():
    print("Bot is online!")

@bot.listen()
@asyncio.coroutine
def on_message(message):
    print(format_ts() + " [" + message.guild.name + "]<" + message.author.nick + ">: " + re.sub(r'[^\x00-\x7F]+','{emoji}', message.content))

@bot.command()
@asyncio.coroutine
def privilege(ctx):
    if not isAuthed(ctx.message, settings, ctx.guild.name):
        yield from ctx.message.channel.send("You are a normal user, no admin operations may be executed from your account.")
    else:
        yield from ctx.message.channel.send("You may execute any command available on this server.")

@bot.command()
@asyncio.coroutine
def eval(ctx):
    if isAuthed(ctx.message, settings, ctx.guild.name):
        try:
            yield from ctx.message.channel.send("Eval on \"" + ' '.join(i for i in word[1:]) + "\", res: ```" + str(eval(' '.join(i for i in word[1:]))) + "```")
        except Exception as e:
            yield from bot.send("Error: ```" + '\n'.join(traceback.extract_tb(sys.exc_info()[2])[-1]) + "```")
            print(str(e))

bot.run('MjIzMzA0NzU4OTE0NDQ5NDA4.CrKfnA.Gu6du9qXpDzIp0zmANTBEcjJ2M4')

# newCommand
# list
# delCommand
# addAuthRole
# newGame
# guess
# restart
# shutdown
# xp
# attr
# reset
# eval
