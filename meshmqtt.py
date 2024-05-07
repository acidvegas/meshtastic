#!/usr/bin/env python
# Meshtastic MQTT Interface - Developed by acidvegas in Python (https://acid.vegas/meshtastic)

import argparse
import base64
import logging

try:
	from cryptography.hazmat.backends           import default_backend
	from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
	raise SystemExit('missing the cryptography module (pip install cryptography)')

try:
	from meshtastic import mesh_pb2, mqtt_pb2, portnums_pb2, telemetry_pb2
except ImportError:
	raise SystemExit('missing the meshtastic module (pip install meshtastic)')

try:
	import paho.mqtt.client as mqtt
except ImportError:
	raise SystemExit('missing the paho-mqtt module (pip install paho-mqtt)')


# Initialize the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S')


class MeshtasticMQTT(object):
	def __init__(self):
		'''Initialize the Meshtastic MQTT client'''

		self.broadcast_id = 4294967295
		self.key = None


	def connect(self, broker: str, port: int, root: str, tls: bool, username: str, password: str, key: str):
		'''
		Connect to the MQTT broker

		:param broker:   The MQTT broker address
		:param port:     The MQTT broker port
		:param root:     The root topic to subscribe to
		:param tls:      Enable TLS/SSL
		:param username: The MQTT username
		:param password: The MQTT password
		:param key:      The encryption key
		'''

		client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='', clean_session=True, userdata=None)
		client.username_pw_set(username=username, password=password)

		self.key = '1PG7OiApB1nwvP+rz05pAQ==' if key == 'AQ==' else key

		if tls:
			client.tls_set()
			#client.tls_insecure_set(False)

		client.on_connect     = self.on_connect
		client.on_message     = self.on_message
		client.on_subscribe   = self.on_subscribe
		client.on_unsubscribe = self.on_unsubscribe

		client.connect(broker, port, 60)
		client.subscribe(root, 0)
		client.loop_forever()


	def decrypt_message_packet(self, message_packet):
		'''
		Decrypt an encrypted message packet.
		
		:param message_packet: The message packet to decrypt
		'''

		# Ensure the key is formatted and padded correctly before turning it into bytes
		padded_key = self.key.ljust(len(self.key) + ((4 - (len(self.key) % 4)) % 4), '=')
		key        = padded_key.replace('-', '+').replace('_', '/')
		key_bytes  = base64.b64decode(key.encode('ascii'))

		# Extract the nonce from the packet
		nonce_packet_id = getattr(message_packet, 'id').to_bytes(8, 'little')
		nonce_from_node = getattr(message_packet, 'from').to_bytes(8, 'little')
		nonce           = nonce_packet_id + nonce_from_node

		# Decrypt the message
		cipher          = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
		decryptor       = cipher.decryptor()
		decrypted_bytes = decryptor.update(getattr(message_packet, 'encrypted')) + decryptor.finalize()

		# Parse the decrypted message
		data = mesh_pb2.Data()
		data.ParseFromString(decrypted_bytes)
		message_packet.decoded.CopyFrom(data)

		return message_packet


	def on_connect(self, client, userdata, flags, rc, properties):
		'''
		Callback for when the client receives a CONNACK response from the server.

		:param client:     The client instance for this callback
		:param userdata:   The private user data as set in Client() or user_data_set()
		:param flags:      Response flags sent by the broker
		:param rc:         The connection result
		:param properties: The properties returned by the broker
		'''

		if rc == 0:
			logging.info('Connected to MQTT broker')
		else:
			logging.error(f'Failed to connect to MQTT broker: {rc}')


	def on_message(self, client, userdata, msg):
		'''
		Callback for when a message is received from the server.

		:param client:   The client instance for this callback
		:param userdata: The private user data as set in Client() or user_data_set()
		:param msg:      An instance of MQTTMessage. This is a
		'''

		# Define the service envelope
		service_envelope = mqtt_pb2.ServiceEnvelope()

		try:
			# Parse the message payload
			service_envelope.ParseFromString(msg.payload)

#			logging.info('Received a packet:')
#			logging.info(service_envelope)

			# Extract the message packet from the service envelope
			message_packet = service_envelope.packet

		except Exception as e:
			#logging.error(f'Failed to parse message: {str(e)}')
			return

		# Check if the message is encrypted before decrypting it
		if message_packet.HasField('encrypted') and not message_packet.HasField('decoded'):
			message_packet = self.decrypt_message_packet(message_packet)

			if message_packet.decoded.portnum == portnums_pb2.TEXT_MESSAGE_APP:
				text_payload = message_packet.decoded.payload.decode('utf-8')
				text = {
					'message' : text_payload,
					'from'    : getattr(message_packet, 'from'),
					'id'      : getattr(message_packet, 'id'),
					'to'      : getattr(message_packet, 'to')
				}
				logging.info('Received text message:')
				logging.info(text)

			h = [portnums_pb2.REMOTE_HARDWARE_APP, portnums_pb2.ROUTING_APP, 

			elif message_packet.decoded.portnum == portnums_pb2.MAP_REPORT_APP: # comes unencrypted
				pos = mesh_pb2.Position()
				pos.ParseFromString(message_packet.decoded.payload)
				logging.info('Received map report:')
				logging.info(pos)

			elif message_packet.decoded.portnum == portnums_pb2.NODEINFO_APP:
				info = mesh_pb2.User()
				info.ParseFromString(message_packet.decoded.payload)
				logging.info('Received node info:')
				logging.info(info)

			elif message_packet.decoded.portnum == portnums_pb2.POSITION_APP:
				pos = mesh_pb2.Position()
				pos.ParseFromString(message_packet.decoded.payload)
				logging.info('Received position:')
				logging.info(pos)

			elif message_packet.decoded.portnum == portnums_pb2.TELEMETRY_APP:
				env = telemetry_pb2.Telemetry()
				env.ParseFromString(message_packet.decoded.payload)
				logging.info('Received telemetry:')
				logging.info(env)

			elif message_packet.decoded.portnum == portnums_pb2.TRACEROUTE_APP:
				routeDiscovery = mesh_pb2.RouteDiscovery()
				routeDiscovery.ParseFromString(message_packet.decoded.payload)
				logging.info('Received traceroute:')
				logging.info(routeDiscovery)

			else:
				logging.warning('Received an unknown message:')
				logging.info(message_packet)

		# If the message is not encrypted, log the payload (this should not happen)
		else:
			logging.warning('Received an unencrypted message')
			logging.info(f'Payload: {message_packet}')


	def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
		'''
		Callback for when the client receives a SUBACK response from the server.

		:param client:           The client instance for this callback
		:param userdata:         The private user data as set in Client() or user_data_set()
		:param mid:              The message ID of the subscribe request
		:param reason_code_list: A list of SUBACK reason codes
		:param properties:       The properties returned by the broker
		'''

		# Since we subscribed only for a single channel, reason_code_list contains a single entry
		if reason_code_list[0].is_failure:
			logging.error(f'Broker rejected you subscription: {reason_code_list[0]}')
		else:
			logging.info(f'Broker granted the following QoS: {reason_code_list[0].value}')


	def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
		'''
		Callback for when the client receives a UNSUBACK response from the server.

		:param client:           The client instance for this callback
		:param userdata:         The private user data as set in Client() or user_data_set()
		:param mid:              The message ID of the unsubscribe request
		:param reason_code_list: A list of UNSUBACK reason codes
		:param properties:       The properties returned by the broker
		'''

		# reason_code_list is only present in MQTTv5, it will always be empty in MQTTv3
		if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
			logging.info('Broker accepted the unsubscription(s)')
		else:
			logging.error(f'Broker replied with failure: {reason_code_list[0]}')

		# Disconnect from the broker
		client.disconnect()



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Meshtastic MQTT Interface')
	parser.add_argument('--broker', default='mqtt.meshtastic.org', help='MQTT broker address')
	parser.add_argument('--port', default=1883, type=int, help='MQTT broker port')
	parser.add_argument('--root', default='#', help='Root topic')
	parser.add_argument('--tls', action='store_true', help='Enable TLS/SSL')
	parser.add_argument('--username', default='meshdev', help='MQTT username')
	parser.add_argument('--password', default='large4cats', help='MQTT password')
	parser.add_argument('--key', default='AQ==', help='Encryption key')
	args = parser.parse_args()

	client = MeshtasticMQTT()
	client.connect(args.broker, args.port, args.root, args.tls, args.username, args.password, args.key)