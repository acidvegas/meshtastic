#!/usr/bin/env python
# Meshtastic Serial Interface - Developed by Acidvegas in Python (https://git.acid.vegas)

import argparse
import logging
import os
import time

try:
	import meshtastic
	from meshtastic.serial_interface import SerialInterface
	from meshtastic.util             import findPorts
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


class Meshtastic(object):
	def __init__(self, serial: str):
		self.interface = None   # We will define the interface in the run() function
		self.nodes     = {}     # Nodes will populate with the on_node() callback
		self.serial    = serial # Serial device to use for the Meshtastic interface
		

	def disconnect(self):
		'''Disconnect from the Meshtastic interface'''

		if pub.getDefaultTopicMgr().hasSubscribers(): 
			pub.unsubAll()
			logging.info('Unsubscribed from all Meshtastic topics')
		else:
			logging.warning('No Meshtastic topics to unsubscribe from')

		if self.interface:
			self.interface.close()
			logging.info('Meshtastic interface closed')
		else:
			logging.warning('No Meshtastic interface to close')


	def run(self):
		'''Start the Meshtastic interface and subscribe to the callback functions'''
		
		if devices := findPorts():
			if not os.path.exists(args.serial) or not args.serial in devices:
				raise SystemExit(f'Invalid serial device: {args.serial} (Available: {devices})') # Show available devices if the specified device is invalid
		else:
			raise SystemExit('No serial devices found')

		# Initialize the Meshtastic interface
		self.interface = SerialInterface(self.serial)

		logging.info('Meshtastic interface started over serial on {self.serial}')

		# Get the current node information
		me = self.interface.nodes[self.interface.myInfo.my_node_num]
		logging.debug(me)
		
		# Create the Meshtastic callback subscriptions
		pub.subscribe(self.event_connect,    'meshtastic.connection.established')
		pub.subscribe(self.event_disconnect, 'meshtastic.connection.lost')
		pub.subscribe(self.on_node,          'meshtastic.node.updated')
		pub.subscribe(self.on_packet,        'meshtastic.receive')

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

		logging.info('Connection established')


	def event_disconnect(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for connection lost

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		logging.warning('Connection lost')


	def on_packet(self, packet: dict):
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


	def on_node(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for node updates

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		if not interface.nodes:
			logging.warning('No nodes found')
			return

		for node in interface.nodes.values():
			short = node['user']['shortName']
			long  = node['user']['longName'].encode('ascii', 'ignore').decode().rstrip()
			num   = node['num']
			id    = node['user']['id']
			mac   = node['user']['macaddr']
			hw    = node['user']['hwModel']

			self.nodes[num] = long # we store the node updates in a dictionary so we can parse the names of who sent incomming messages



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Meshtastic Interface')
	parser.add_argument('--serial', default='/dev/ttyACM0', help='Use serial interface')
	args = parser.parse_args()

	# Define the Meshtastic client
	mesh = Meshtastic(args.serial)

	# Initialize the Meshtastic interface
	mesh.run()

	# Keep-alive loop
	try:
		while True:
			time.sleep(60)
	except KeyboardInterrupt:
		pass
	finally:
		mesh.disconnect()
