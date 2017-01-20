import discord
import asyncio
import select
import time
import sys,struct

class Responder(discord.Client):
    def __init__(self, token, channel):
        super().__init__()
        self.token = token
        self.q = asyncio.Queue()
        self.asyncio_loop = asyncio.get_event_loop()
        self.asyncio_loop.add_reader(sys.stdin, self.on_terminal_msg, self.q)
        self.is_ready = False
        self.to_send = []
        self.channel_id = channel
        self.current_buffer = ''
    
    def on_terminal_msg(self, queue):
        if self.is_ready == True:
            current_input = sys.stdin.readline()
            self.current_buffer += current_input
            
            self.current_buffer = self.current_buffer.strip()
            
            if not self.current_buffer == '':
                self.to_send = self.to_send + [self.current_buffer]
                sys.stdout.write('> ')
            else:
                sys.stdout.write('> ')
            self.current_buffer = ''
        else:
            pass


    @asyncio.coroutine
    def on_message(self, message):
        if message.channel.id == self.channel_id and self.is_ready == True:
            if not message.author.id == self.user.id:
                content = sys.stdin.readline()
                sys.stdout.write('\r'+'] ')
                sys.stdout.write(message.author.name + ': ' + message.content + '\n> ')

    def initiate(self):
        sys.stdout.flush()
        sys.stdout.write('Initiating Connection to Discord...')
        sys.stdout.flush()
        try:
            self.loop.run_until_complete(self.start(self.token, bot=True))
        except discord.errors.LoginFailure:
            print('broke...')


    @asyncio.coroutine
    def on_ready(self):
        self.is_ready = True
        sys.stdout.write('\rConnected to Discord!              \n> ')
    
        yield from self.looper()

    @asyncio.coroutine
    def looper(self):
        while True:
            if len(self.to_send) > 0:
                var = self.to_send[0]
                del self.to_send[0]
                yield from self.send_message(self.get_channel(self.channel_id), var, tts=False)

            yield from asyncio.sleep(0.2)



client = Responder('xe27at0hKMGZdLmJTh9iFPVjqpT1tj2S', 'bot_testing')
client.initiate()
