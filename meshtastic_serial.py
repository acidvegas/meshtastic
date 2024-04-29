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
	from meshtastic.tcp_interface    import TCPInterface		
except ImportError:
	raise ImportError('meshtastic library not found (pip install meshtastic)')

try:
	from pubsub import pub
except ImportError:
	raise ImportError('pubsub library not found (pip install pypubsub)')


# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)9s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %I:%M:%S')


class MeshtasticClient(object):
	def __init__(self):
		self.interface = None
		self.me        = {} 
		self.nodes     = {}


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


	def sendmsg(self, message: str, destination: int, channelIndex: int = 0):
		'''
		Send a message to the Meshtastic interface

		:param message: The message to send
		'''

		if len(message) > 255:
			logging.warning('Message exceeds 255 characters')
			message = message[:255]

		self.interface.sendText(message, destination, wantAck=True, channelIndex=channelIndex) # Do we need wantAck?

		logging.info(f'Sent broadcast message: {message}')


	def listen(self):
		'''Create the Meshtastic callback subscriptions'''

		pub.subscribe(self.event_connect,    'meshtastic.connection.established')
		pub.subscribe(self.event_data,       'meshtastic.receive.data.portnum')
		pub.subscribe(self.event_disconnect, 'meshtastic.connection.lost')
		pub.subscribe(self.event_node,       'meshtastic.node')
		pub.subscribe(self.event_position,   'meshtastic.receive.position')
		pub.subscribe(self.event_text,       'meshtastic.receive.text')
		pub.subscribe(self.event_user,       'meshtastic.receive.user')

		logging.debug('Listening for Meshtastic events...')
		
		
	def event_connect(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for connection established

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		logging.info(f'Connected to the {self.me["user"]["longName"]} radio on {self.me["user"]["hwModel"]} hardware')
		logging.info(f'Found a total of {len(self.nodes):,} nodes')


	def event_data(self, packet: dict, interface):
		'''
		Callback function for data updates

		:param packet: Data information
		:param interface: Meshtastic interface
		'''

		logging.info(f'Data update: {packet}')


	def event_disconnect(self, interface, topic=pub.AUTO_TOPIC):
		'''
		Callback function for connection lost

		:param interface: Meshtastic interface
		:param topic:     PubSub topic
		'''

		logging.warning('Lost connection to radio!')

		time.sleep(10)

		 # TODO: Consider storing the interface option and value in a class variable since we don't want to reference the args object inside the class
		self.connect('serial' if args.serial else 'tcp', args.serial if args.serial else args.tcp)

	
	def event_node(self, node):
		'''
		Callback function for node updates

		:param node: Node information
		'''

		self.nodes[node['num']] = node

		logging.info(f'Node recieved: {node["user"]["id"]} - {node["user"]["shortName"].ljust(4)} - {node["user"]["longName"]}')


	def event_position(self, packet: dict, interface):
		'''
		Callback function for position updates

		:param packet: Position information
		:param interface: Meshtastic interface
		'''

		sender    = packet['from']
		msg       = packet['decoded']['payload'].hex() # What exactly is contained in this payload?
		id        = self.nodes[sender]['user']['id']       if sender in self.nodes else '!unk   '
		name      = self.nodes[sender]['user']['longName'] if sender in self.nodes else 'UNK'
		longitude = packet['decoded']['position']['longitudeI'] / 1e7
		latitude  = packet['decoded']['position']['latitudeI'] / 1e7
		altitude  = packet['decoded']['position']['altitude']
		snr	      = packet['rxSnr']
		rssi	  = packet['rxRssi']

		logging.info(f'Position recieved: {id} - {name}: {longitude}, {latitude}, {altitude}m (SNR: {snr}, RSSI: {rssi}) - {msg}')


	def event_text(self, packet: dict, interface):
		'''
		Callback function for received packets

		:param packet: Packet received
		'''

		sender = packet['from']
		to     = packet['to'] 
		msg    = packet['decoded']['payload'].decode('utf-8')
		id     = self.nodes[sender]['user']['id']       if sender in self.nodes else '!unk   '
		name   = self.nodes[sender]['user']['longName'] if sender in self.nodes else 'UNK'
		target = self.nodes[to]['user']['longName']     if to     in self.nodes else 'UNK'

		logging.info(f'Message recieved: {id} {name} -> {target}: {msg}')
		print(packet)


	def event_user(self, packet: dict, interface):
		'''
		Callback function for user updates

		:param user: User information
		'''

		'''
		{
			'from' : 862341900,
			'to'   : 4294967295,
			'decoded' : {
				'portnum'      : 'NODEINFO_APP',
				'payload'      : b'\n\t!33664b0c\x12\x08HELLDIVE\x1a\x04H3LL"\x06d\xe83fK\x0c(+8\x03',
				'wantResponse' : True,
				'user' : {
					'id'        : '!33664b0c',
					'longName'  : 'HELLDIVE',
					'shortName' : 'H3LL',
					'macaddr'   : 'ZOgzZksM',
					'hwModel'   : 'HELTEC_V3',
					'role'      : 'ROUTER_CLIENT',
					'raw'       : 'rm this'
				}
			},
			'id'       : 1612906268,
			'rxTime'   : 1714279638,
			'rxSnr'    : 6.25,
			'hopLimit' : 3,
			'rxRssi'   : -38,
			'hopStart' : 3,
			'raw'      : 'rm this'
		}
		'''

		# Not sure what to do with this yet...
		pass



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
		try:
			mesh.interface.close()
		except:
			pass
	finally:
		logging.info('Connection to radio lost')

'''
Notes:
		conf = self.interface.localNode.localConfig
		ok = interface.getNode('^local')
		print(ok.channels)
'''