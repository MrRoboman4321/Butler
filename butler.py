import discord, random, asyncio, pickle, os, os.path, re
 
client = discord.Client()
settings = {}
servers = []
#settings = {'commands': [command, output], 'authedRoles': [role1, role2], 'reminders', [r1, r2]}
 
def saveSettings(settings, server):
    pickle.dump(settings[server], open('./settings/' + str(server) + '.bot', 'wb'))
 
def isAuthed(message, settings, server):
    if message.author.name == "Ronoman":
        return True
    for i in settings[server]['authedRoles']:
        for j in message.author.roles:
            if i == j.name:
                return True
    return False
   
@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global settings
    try:
        settings = {}
        for i in os.listdir('./settings'):
            name = i.split('.')[0]
            servers.append(name)
            settings[name] = pickle.load(open("./settings/" + name + ".bot", 'rb'))
        print(settings)
    except EOFError:
        print("EOFError")
        settings = {}
   
@client.event
@asyncio.coroutine
def on_message(message):
    global settings
	
    if message.server.id not in servers:
        servers.append(message.server.id)
        settings[message.server.id] = {'commands': [], 'authedRoles': [], 'data': {}}
        saveSettings(settings, message.server.id)
    server = message.server.id
	
    print("[" + message.server.name + "]:[" + message.channel.name + "] <" + message.author.name + ">: " + re.sub(r'[^\x00-\x7F]+','{emoji}', message.content))
	
    if message.content.startswith("!"): #If its a command
        if(message.author.name != "Butler"): #If its not from me
            message.content = message.content[1:] #Remove the !
            word = message.content.split(" ") #Split up all the words into a list
			
            for i in settings[server]['commands']: #Execute all text commands
                if(word[0] == i[0]):
                    yield from client.send_message(message.channel, i[1])
					
            if(word[0] == "newCommand"): #For a new listed command
                if(isAuthed(message, settings, server)):
                    settings[server]['commands'].append([word[1],' '.join(word[2:])]) #Add the new command with all the text after concatenated with spaces
                    saveSettings(settings, server)
                    yield from client.send_message(message.channel, "Command " + word[1] + " added!")
					
            elif(word[0] == "list"): #List all the commands
                temp = "Commands:\n"
                for i in settings[server]['commands']:
                    temp = temp + i[0] + ": " + i[1] + "\n" #commandName: commandText
                yield from client.send_message(message.channel, temp)
					
            elif(word[0] == "delCommand"):
                if(isAuthed(message, settings, server)):
                    for i in settings[server]['commands']:
                        if(i[0] == word[1]):
                            settings[server]['commands'].remove(i)
                            yield from client.send_message(message.channel, "Command " + i[0] + " removed.")
							
            elif(word[0] == "addAuthRole"): #Add new auth role
                if(isAuthed(message, settings, server)):
                    settings[server]['authedRoles'].append(''.join(word[1:]))
                    saveSettings(settings, server)
                    yield from client.send_message(message.channel, "Added " + ''.join(word[1:]) + " to authenticated roles.")
					
            elif(word[0] == "privilege"):
                if(not isAuthed(message, settings, server)):
                    yield from client.send_message(message.channel, "You are a normal user, no admin operations may be executed from your account.")
                else:
                    yield from client.send_message(message.channel, "You may execute any command available on this server.")


    elif(message.content.lower().startswith("hello butler")): #Response to a nice hello
        if(not message.channel.is_private):
            yield from client.send_message(message.channel, "Hello " + message.author.top_role.name + ".")
                                                               
client.run('MjIzMzA0NzU4OTE0NDQ5NDA4.CrKfnA.Gu6du9qXpDzIp0zmANTBEcjJ2M4')