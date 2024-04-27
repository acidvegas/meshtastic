#!/usr/bin/env python
# Meshtastic Serial Interface - Developed by Acidvegas in Python (https://git.acid.vegas/meshtastic)

import argparse
import logging
import os
import time

try:
	import meshtastic
	from meshtastic.serial_interface import SerialInterface
	from meshtastic.util             import findPorts
	from meshtastic.tcp_interface    import TCPInterface
except ImportError:
	raise ImportError('meshtastic library not found (pip install meshtastic)')

try:
	from pubsub import pub
except ImportError:
	raise ImportError('pubsub library not found (pip install pypubsub)') # Confirm this Pypi package name...


# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)9s | %(funcName)s | %(message)s')


def now():
	'''Returns the current date and time in a formatted string'''

	return time.strftime('%Y-%m-%d %H:%M:%S')


class MeshtasticClient(object):
	def __init__(self):
		self.interface = None # We will define the interface in the connect() function
		self.me        = {}   # We will populate this with the event_connect() callback
		self.nodes     = {}   # Nodes will populate with the event_node() callback


	def connect(self, option: str, value: str):
		'''
  		Connect to the Meshtastic interface

		:param option: The interface option to connect to
		:param value:  The value of the interface option
	 	'''

		while True:
			try:
				if option == 'serial':
					if devices := findPorts():
						if not os.path.exists(args.serial) or not args.serial in devices:
							raise Exception(f'Invalid serial port specified: {args.serial} (Available: {devices})')
					else:
						raise Exception('No serial devices found')
					self.interface = SerialInterface(value)

				elif option == 'tcp':
					self.interface = TCPInterface(value)

				else:
					raise SystemExit('Invalid interface option')

			except Exception as e:
				logging.error(f'Failed to connect to the Meshtastic interface: {e}')
				logging.error('Retrying in 10 seconds...')
				time.sleep(10)

			else:
				self.me = self.interface.getMyNodeInfo()
				break


	def send(self, message: str):
		'''
		Send a message to the Meshtastic interface

		:param message: The message to send
		'''

		if len(message) > 255:
			logging.warning('Message exceeds 255 characters')
			message = message[:255]

		self.interface.sendText(message)

		logging.info(f'Sent broadcast message: {message}')


	def listen(self):
		'''Create the Meshtastic callback subscriptions'''

		pub.subscribe(self.event_connect,    'meshtastic.connection.established')
		pub.subscribe(self.event_disconnect, 'meshtastic.connection.lost')
		pub.subscribe(self.event_node,       'meshtastic.node')
		pub.subscribe(self.event_packet,     'meshtastic.receive')

		logging.debug('Listening for Meshtastic events...')

		# The meshtastic.receive topics can be broken down further:
		# pub.subscribe(self.on_text,      'meshtastic.receive.text')
		# pub.subscribe(self.on_position,  'meshtastic.receive.position')
		# pub.subscribe(self.on_user,      'meshtastic.receive.user')
		# pub.subscribe(self.on_data,      'meshtastic.receive.data.portnum')


	def event_connect(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for connection established

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		logging.info(f'Connected to the {self.me["user"]["longName"]} radio on {self.me["user"]["hwModel"]} hardware')
		logging.info(f'Found a total of {len(self.nodes):,} nodes')


	def event_disconnect(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for connection lost

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		logging.warning('Lost connection to radio!')
		logging.info('Reconnecting in 10 seconds...')

		time.sleep(10)

		 # TODO: Consider storing the interface option and value in a class variable since we don't want to reference the args object inside the class
		self.connect('serial' if args.serial else 'tcp', args.serial if args.serial else args.tcp)



	def event_node(self, node):
		'''
		Callback function for node updates

		:param node: Node information
		'''

		self.nodes[node['num']] = node

		logging.info(f'Node found: {node["user"]["id"]} - {node["user"]["shortName"].ljust(4)} - {node["user"]["longName"]}')


	def event_packet(self, packet: dict):
		'''
		Callback function for received packets

		:param packet: Packet received
		'''

		# Handle incoming text messages
		if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
			sender = packet['from']
			msg    = packet['decoded']['payload'].decode('utf-8')

			# Message from self
			if sender == self.interface.myInfo.my_node_num:
				print(f'{now()} {self.nodes[sender]}: {msg}') # Can do custom formatting here or ignore the message, just an example

			# Message from others
			if sender in self.nodes:
				print(f'{now()} {self.nodes[sender]}: {msg}')

			# Unknown sender
			else:
				# TODO: Trigger request for node update here
				print(f'{now()} UNK: {msg}')



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Meshtastic Interfacing Tool')
	parser.add_argument('--serial', help='Use serial interface') # Typically /dev/ttyUSB0 or /dev/ttyACM0
	parser.add_argument('--tcp',    help='Use TCP interface')    # Can be an IP address or hostname (meshtastic.local)
	args = parser.parse_args()

	# Ensure one interface is specified
	if (not args.serial and not args.tcp) or (args.serial and args.tcp):
		raise SystemExit('Must specify either --serial or --tcp interface')

	# Initialize the Meshtastic client
	mesh = MeshtasticClient()

	# Listen for Meshtastic events
	mesh.listen()

	# Connect to the Meshtastic interface
	mesh.connect('serial' if args.serial else 'tcp', args.serial if args.serial else args.tcp)

	# Keep-alive loop
	try:
		while True:
			time.sleep(60)
	except KeyboardInterrupt:
		pass # Exit the loop on Ctrl+C
	finally:
		if mesh.interface:
			try:
				mesh.interface.close()
				logging.info('Connection to radio interface closed!')
			except:
				pass
