#!/usr/bin/env python
# meshtastic irc relay - developed by acidvegas in python (https://git.acid.vegas/meshtastic)

import argparse
import asyncio
import logging
import ssl
import time

# EF576MkXA3aEURbCfNn6p0FfZdua4I

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'


# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')


def color(msg: str, foreground: str, background: str = None) -> str:
	'''
	Color a string with the specified foreground and background colors.

	:param msg: The string to color.
	:param foreground: The foreground color to use.
	:param background: The background color to use.
	'''

	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'


class Bot():
	def __init__(self):
		self.nickname = 'MESHTASTIC'
		self.reader   = None
		self.writer   = None
		self.last     = time.time()


	async def action(self, chan: str, msg: str):
		'''
		Send an ACTION to the IRC server.

		:param chan: The channel to send the ACTION to.
		:param msg: The message to send to the channel.
		'''

		await self.sendmsg(chan, f'\x01ACTION {msg}\x01')


	async def raw(self, data: str):
		'''
		Send raw data to the IRC server.

		:param data: The raw data to send to the IRC server. (512 bytes max including crlf)
		'''

		await self.writer.write(data[:510].encode('utf-8') + b'\r\n')


	async def sendmsg(self, target: str, msg: str):
		'''
		Send a PRIVMSG to the IRC server.

		:param target: The target to send the PRIVMSG to. (channel or user)
		:param msg: The message to send to the target.
		'''

		await self.raw(f'PRIVMSG {target} :{msg}')


	async def connect(self):
		'''Connect to the IRC server.'''

		while True:
			try:
				options = {
					'host'       : args.server,
					'port'       : args.port,
					'limit'      : 1024,
					'ssl'        : ssl._create_unverified_context() if args.ssl else None, # TODO: Do not use the args variable here
					'family'     : 2, # AF_INET = 2, AF_INET6 = 10
					'local_addr' : None
				}

				self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**options), 15)

				await self.raw(f'USER MESHT 0 * :git.acid.vegas/meshtastic') # Static for now
				await self.raw('NICK ' + self.nickname)

				while not self.reader.at_eof():
					data = await asyncio.wait_for(self.reader.readuntil(b'\r\n'), 300)
					await self.handle(data.decode('utf-8').strip())

			except Exception as ex:
				logging.error(f'failed to connect to {args.server} ({str(ex)})')

			finally:
				await asyncio.sleep(15)


	async def eventPRIVMSG(self, data: str):
		'''
		Handle the PRIVMSG event.

		:param data: The data received from the IRC server.
		'''

		parts  = data.split()

		ident  = parts[0][1:]
		nick   = parts[0].split('!')[0][1:]
		target = parts[2]
		msg	   = ' '.join(parts[3:])[1:]

		if target == args.channel: # TODO: Don't use the args variable here
			if msg.startswith('!'):
				if time.time() - self.last < 3:
					if not self.slow:
						self.slow = True
						await self.sendmsg(target, color('Slow down nerd!', red))
				else:
					self.slow = False
					parts = msg.split()
					if parts[0] == '!meshage' and len(parts) > 1:
						message = ' '.join(parts[1:])
						if len(message) > 255:
							await self.sendmsg(target, color('Message exceeds 255 bytes nerd!', red))
						# TODO: Send a meshtastic message (We have to ensure our outbounds from IRC don't loop back into IRC)

					self.last = time.time() # Update the last command time if it starts with ! character to prevent command flooding


	async def handle(self, data: str):
		'''
		Handle the data received from the IRC server.

		:param data: The data received from the IRC server.
		'''

		logging.info(data)

		try:
			parts = data.split()

			if parts[0] == 'PING':
				await self.raw('PONG ' + parts[1])

			elif parts[1] == '001': # RPL_WELCOME
				await self.raw(f'MODE {self.nickname} +B')
				await self.sendmsg('NickServ', f'IDENTIFY {self.nickname} simps0nsfan420')
				await asyncio.sleep(10) # Wait for NickServ to identify or any channel join delays
				await self.raw(f'JOIN {args.channel} {args.key if args.key else ""}')

			elif parts[1] == '433': # ERR_NICKNAMEINUSE
				self.nickname += '_' # revamp this to be more unique
				await self.raw('NICK ' + self.nickname)

			elif parts[1] == 'INVITE':
				target = parts[2]
				chan   = parts[3][1:]
				if target == self.nickname and chan == args.channel:
					await self.raw(f'JOIN {chan}')

			elif parts[1] == 'KICK':
				chan   = parts[2]
				kicked = parts[3]
				if kicked == self.nickname and chan == args.channel:
					await asyncio.sleep(3)
					await self.raw(f'JOIN {args.channel} {args.key if args.key else ""}')

			elif parts[1] == 'PRIVMSG':
				await self.eventPRIVMSG(data) # We put this in a separate function since it will likely be the most used/handled event

		except (UnicodeDecodeError, UnicodeEncodeError):
			pass

		except Exception as ex:
			logging.exception(f'Unknown error has occured! ({ex})')



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Connect to an IRC server.')
	parser.add_argument('server', help='The IRC server address.')
	parser.add_argument('channel', help='The IRC channel to join.')
	parser.add_argument('--port', type=int, help='The port number for the IRC server.')
	parser.add_argument('--ssl', action='store_true', help='Use SSL for the connection.')
	parser.add_argument('--key',  default='', help='The key (password) for the IRC channel, if required.')
	args = parser.parse_args()

	if not args.channel.startswith('#'):
		channel = '#' + args.channel

	if not args.port:
		args.port = 6697 if args.ssl else 6667
	elif args.port < 1 or args.port > 65535:
		raise ValueError('Port must be between 1 and 65535.')

	print(f'Connecting to {args.server}:{args.port} (SSL: {args.ssl}) and joining {args.channel} (Key: {args.key or 'None'})')

	bot = Bot()

	asyncio.run(bot.connect())
