import discord, random, asyncio, pickle, os, os.path, re, random, sys, datetime, traceback
from subprocess import Popen
print(discord.__version__)
client = discord.Client()
settings = {}
servers = []
users = {}
 
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
   
class Game():
    def __init__(self, client, message):
        self.user = message.author.id
        self.client = client
        self.channel = message.channel
    def parseMessage(self, message, command):
        pass
        
    @asyncio.coroutine
    def sendMessage(self, message, channel):
        yield from self.client.send_message(channel, message)
   
guessingGames = {}
class GuessingGame(Game):
    def __init__(self, client, message):
        super(GuessingGame, self).__init__(client, message)
        self.number = random.randint(1, 20)
        print("Number: " + str(self.number))
        self.tries = 0
        client.loop.create_task(self.sendMessage("Counting game started!", self.channel))

    def parseMessage(self, message, command):
        if message.author.id == self.user and message.channel == self.channel:
            guessed = int(command[1])
            if command[0] == "guess" :
                if guessed > 20 or guessed < 1:
                    client.loop.create_task(self.sendMessage("Please enter a number between 1-20.", message.channel))
                elif guessed < self.number:
                    self.tries += 1
                    client.loop.create_task(self.sendMessage("Too low! Total Tries: " + str(self.tries), message.channel))
                elif guessed > self.number:
                    self.tries += 1
                    client.loop.create_task(self.sendMessage("Too high! Total Tries: " + str(self.tries), message.channel))
                elif guessed == self.number:
                    self.tries += 1
                    guessingGames.pop(message.author.id + message.channel.id, None)
                    client.loop.create_task(self.sendMessage("You got it right! Total tries: " + str(self.tries), message.channel))

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global settings
    global users
    try:
        settings = {}
        for i in os.listdir('./settings/servers'):
            name = i.split('.')[0]
            servers.append(name)
            settings[name] = pickle.load(open("./settings/servers/" + name + ".svr", 'rb'))
        
    except EOFError:
        print("EOFError")
        settings = {}

    try:
        users = {}
        for i in os.listdir('./settings/users'):
            name = i.split('.')[0]
            users[name] = pickle.load(open('./settings/users/' + name + '.usr', 'rb'))
    except EOFError:
        print("EOFError")
        users = {}
    if len(sys.argv) > 1:
        yield from client.send_message(client.get_channel(sys.argv[1]), "Restarted!")
   
@client.event
@asyncio.coroutine
def on_message(message):
    global settings
    
    if message.server.id not in servers:
        servers.append(message.server.id)
        settings[message.server.id] = {'commands': [], 'authedRoles': [], 'data': {}}
        saveSettings(settings, message.server.id)

    if message.author.id in users:
        if message.server.id not in users[message.author.id]:
            users[message.author.id][message.server.id] = {}
            saveUsers(users, message.author.id)
    else:
        users[message.author.id] = {}
        if message.server.id not in users[message.author.id]:
            users[message.author.id][message.server.id] = {}
            saveUsers(users, message.author.id)
    saveUsers(users, message.author.id)
    server = message.server.id
    
    print("[" + message.server.name + "]:[" + message.channel.name + "] <" + message.author.name + ">: " + re.sub(r'[^\x00-\x7F]+','{emoji}', message.content))

    #-----START XP RANKING-----#
    if 'lastXp' in users[message.author.id][message.server.id] and message.author.nick != message.server.me.nick:
        total_seconds = (datetime.datetime.now() - users[message.author.id][message.server.id]['lastXp']).total_seconds()
        if total_seconds > 60:
            users[message.author.id][message.server.id]['xp'] += 1
            users[message.author.id][message.server.id]['lastXp'] = datetime.datetime.now()

            if users[message.author.id][message.server.id]['xp'] >= users[message.author.id][message.server.id]['nextRank']:
                users[message.author.id][message.server.id]['rank'] += 1
                next = users[message.author.id][message.server.id]['nextRank']
                users[message.author.id][message.server.id]['nextRank'] += users[message.author.id][message.server.id]['prevRank']
                users[message.author.id][message.server.id]['prevRank'] = next
                yield from client.send_message(message.channel, "Rank up! New rank: " + str(users[message.author.id][message.server.id]['rank']))
            saveUsers(users, message.author.id)
    elif message.author.nick != message.server.me.nick:
        users[message.author.id][message.server.id]['lastXp'] = datetime.datetime.now()
        users[message.author.id][message.server.id]['xp'] = 0
        users[message.author.id][message.server.id]['nextRank'] = 2
        users[message.author.id][message.server.id]['prevRank'] = 1
        users[message.author.id][message.server.id]['rank'] = 1
        saveUsers(users, message.author.id)
        yield from client.send_message(message.channel, "New server! Total xp: " + str(users[message.author.id][message.server.id]['xp']))
    #------END XP RANKING------#

    message.server.me.nick = message.server.me.nick if message.server.me.nick != None else "Butler"

    if message.content.startswith("!"): #If its a command
        if(message.author.nick != message.server.me.nick): #If its not from me
            message.content = message.content[1:] #Remove the !
            word = message.content.split(" ") #Split up all the words into a list
            
            for i in settings[server]['commands']: #Execute all text commands
                if word[0] == i[0] :
                    yield from client.send_message(message.channel, i[1])
                    
            if word[0] == "newCommand": #For a new listed command
                if isAuthed(message, settings, server):
                    settings[server]['commands'].append([word[1],' '.join(word[2:])]) #Add the new command with all the text after concatenated with spaces
                    saveSettings(settings, server)
                    yield from client.send_message(message.channel, "Command " + word[1] + " added!")
                    
            elif word[0] == "list" : #List all the commands
                temp = "Commands:\n"
                for i in settings[server]['commands']:
                    temp = temp + i[0] + ": \n" + i[1] + "\n" #commandName: commandText
                yield from client.send_message(message.channel, temp)
                    
            elif word[0] == "delCommand":
                if isAuthed(message, settings, server):
                    for i in settings[server]['commands']:
                        if i[0] == word[1]:
                            settings[server]['commands'].remove(i)
                            yield from client.send_message(message.channel, "Command " + i[0] + " removed.")
                            
            elif word[0] == "addAuthRole": #Add new auth role
                if isAuthed(message, settings, server):
                    settings[server]['authedRoles'].append(''.join(word[1:]))
                    saveSettings(settings, server)
                    yield from client.send_message(message.channel, "Added " + ''.join(word[1:]) + " to authenticated roles.")
                    
            elif word[0] == "privilege":
                if not isAuthed(message, settings, server):
                    yield from client.send_message(message.channel, "You are a normal user, no admin operations may be executed from your account.")
                else:
                    yield from client.send_message(message.channel, "You may execute any command available on this server.")
            
            elif word[0] == "newGame":
                if (message.author.id + message.channel.id) in guessingGames:
                    yield from client.send_message(message.channel, "You already have a game running! Guess with !guess.")
                else:
                    guessingGames[message.author.id + message.channel.id] = GuessingGame(client, message)
            
            elif word[0] == "guess":
                if (message.author.id + message.channel.id) in guessingGames:
                    guessingGames[message.author.id + message.channel.id].parseMessage(message, word)
                else:
                    yield from client.send_message(message.channel, "Start a game with !newGame first!")
                    
            elif word[0] == "restart":
                if isAuthed(message, settings, server):
                    yield from client.send_message(message.channel, "Restarting!")
                    os.system("C:\Python34\python.exe butler.py " + message.channel.id)
                    sys.exit()

            elif word[0] == "shutdown":
                if isAuthed(message, settings, server):
                    yield from client.send_message(message.channel, "Cya!")
                    sys.exit()

            elif word[0] == "xp" or word[0] == 'rank':
                yield from client.send_message(message.channel, "Total xp for this server: " + str(users[message.author.id][message.server.id]['xp']) + ", Rank: " + str(users[message.author.id][message.server.id]['rank']) + ", Xp until next rank: " + str(users[message.author.id][message.server.id]['nextRank'] - users[message.author.id][message.server.id]['xp']))

            elif word[0] == "attr": #deprecated, use eval
                if isAuthed(message, settings, server):
                    try:
                        if(len(word) > 1):
                            yield from client.send_message(message.channel, "Attr: " + word[1] + ", Val: ```" + str(users[message.author.id][message.server.id][word[1]]) + "```")
                        else:
                            yield from client.send_message(message.channel, "Full user: " + str(users[message.author.id][message.server.id]))
                    except KeyError:
                        yield from client.send_message(message.channel, "Bad key")

            elif word[0] == "reset":
                if isAuthed(message, settings, server):
                    yield from client.send_message(message.channel, "Resetting user " + message.server.get_member(word[1]).display_name + " ...")
                    users[message.author.id][message.server.id] = {}
                    saveUsers(users, message.author.id)
                else:
                    print("nope")

            elif word[0] == "eval":
                if isAuthed(message, settings, server):
                    try:
                        yield from client.send_message(message.channel, "Eval on \"" + ' '.join(i for i in word[1:]) + "\", res: ```" + str(eval(' '.join(i for i in word[1:]))) + "```")
                    except Exception as e:
                        yield from client.send_message(message.channel, "Error: ```" + '\n'.join(traceback.extract_tb(sys.exc_info()[2])[-1]) + "```")
                        print(str(e))


    elif message.content.lower().startswith("hello " + message.server.me.nick) or message.content.lower().startswith("hello butler"): #Response to a nice hello
        if not message.channel.is_private:
            yield from client.send_message(message.channel, "Hello " + message.author.top_role.name + ".")
                                                               
client.run('MjIzMzA0NzU4OTE0NDQ5NDA4.CrKfnA.Gu6du9qXpDzIp0zmANTBEcjJ2M4')
