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


# Global variables
node_long_names = {}

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)9s | %(funcName)s | %(message)s')


def now():
	'''Returns the current date and time in a formatted string'''

	return time.strftime('%Y-%m-%d %H:%M:%S')


def on_connect(interface, topic=pub.AUTO_TOPIC):
	'''
	Callback function for connection established

	:param interface: Meshtastic interface
	:param topic:     PubSub topic
	'''

	logging.info('Connection established')


def on_disconnect(interface, topic=pub.AUTO_TOPIC):
	'''
	Callback function for connection lost

	:param interface: Meshtastic interface
	:param topic:     PubSub topic
	'''

	logging.error('Connection lost')


def on_packet(packet: dict):
	'''
	Callback function for received packets

	:param packet: Packet received
	'''

	if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
		sender_id = str(packet['from'])
		message = packet['decoded']['payload'].decode('utf-8')

		# Message from self
		if sender_id == str(interface.myInfo.my_node_num):
			print(f'{now()} {node_long_names[sender_id]}: {message}')

		# Message from others
		if sender_id in node_long_names:
			print(f'{now()} {node_long_names[sender_id]}: {message}')

		# Unknown message (maybe trigger for rescanning the nodes if we dont find the sender in the list)
		else:
			print(f'{now()} UNK: {message}')


def on_node(interface, topic=pub.AUTO_TOPIC):
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
		num   = str(node['num'])
		id    = node['user']['id']
		mac   = node['user']['macaddr']
		hw    = node['user']['hwModel']

		node_long_names[num] = long # we store the node updates in a dictionary so we can parse the names of who sent incomming messages



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Meshtastic Interface')
	parser.add_argument('--serial', default='/dev/ttyACM0', help='Use serial interface')
	args = parser.parse_args()

	# Check if the serial device exists
	if available_devices := findPorts():
		if not os.path.exists(args.serial) or not args.serial in available_devices:
			raise SystemExit(f'Invalid serial device: {args.serial} (Available: {available_devices})')
	else:
		raise SystemExit('No serial devices found')

	# Initialize the Meshtastic interface
	interface = SerialInterface(args.serial)

	# Create the Meshtastic callback subscriptions
	pub.subscribe(on_connect,    'meshtastic.connection.established')
	pub.subscribe(on_disconnect, 'meshtastic.connection.lost')
	pub.subscribe(on_node,       'meshtastic.node.updated')
	pub.subscribe(on_packet,     'meshtastic.receive')

	# The meshtastic.receive topics can be broken down further:
	# pub.subscribe(on_text,      'meshtastic.receive.text')
	# pub.subscribe(on_position,  'meshtastic.receive.position')
	# pub.subscribe(on_user,      'meshtastic.receive.user')
	# pub.subscribe(on_data,      'meshtastic.receive.data.portnum')

	# Keep-alive loop
	try:
		while True:
			time.sleep(60)
	except KeyboardInterrupt:
		pass
	finally:
		interface.close()
