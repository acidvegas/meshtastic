#!/usr/bin/env python3
# Meshtastic MQTT Interface - Developed by acidvegas in Python (https://acid.vegas/meshtastic)

import argparse
import base64
import logging

try:
	from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
	from cryptography.hazmat.backends import default_backend
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


def process_message(message_packet, text_payload, is_encrypted):

	text = {
		'message': text_payload,
		'from': getattr(message_packet, 'from'),
		'id': getattr(message_packet, 'id'),
		'to': getattr(message_packet, 'to')
	}
	print(text)


def decode_encrypted(message_packet):
	'''
	Decrypt an encrypted message packet.

	:param message_packet: The message packet to decrypt'''
	try:
		key_bytes = base64.b64decode(key.encode('ascii'))

		nonce_packet_id = getattr(message_packet, 'id').to_bytes(8, 'little')
		nonce_from_node = getattr(message_packet, 'from').to_bytes(8, 'little')
		nonce = nonce_packet_id + nonce_from_node

		cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
		decryptor = cipher.decryptor()
		decrypted_bytes = decryptor.update(getattr(message_packet, 'encrypted')) + decryptor.finalize()

		data = mesh_pb2.Data()
		data.ParseFromString(decrypted_bytes)
		message_packet.decoded.CopyFrom(data)

		if message_packet.decoded.portnum == portnums_pb2.TEXT_MESSAGE_APP:
			text_payload = message_packet.decoded.payload.decode('utf-8')
			is_encrypted = True
			process_message(message_packet, text_payload, is_encrypted)
			print(f'{text_payload}')


		elif message_packet.decoded.portnum == portnums_pb2.NODEINFO_APP:
				info = mesh_pb2.User()
				info.ParseFromString(message_packet.decoded.payload)
				print(info)

		elif message_packet.decoded.portnum == portnums_pb2.POSITION_APP:
			pos = mesh_pb2.Position()
			pos.ParseFromString(message_packet.decoded.payload)
			print(pos)

		elif message_packet.decoded.portnum == portnums_pb2.TELEMETRY_APP:
			env = telemetry_pb2.Telemetry()
			env.ParseFromString(message_packet.decoded.payload)
			print(env)

	except Exception as e:
		logging.error(f'Failed to decrypt message: {str(e)}')


def on_connect(client, userdata, flags, rc, properties):
	'''
	Callback for when the client receives a CONNACK response from the server.
	
	:param client: The client instance for this callback
	:param userdata: The private user data as set in Client() or user_data_set()
	:param flags: Response flags sent by the broker
	:param rc: The connection result
	:param properties: The properties returned by the broker
	'''

	if rc == 0:
		print('Connected to MQTT broker')
	else:
		logging.error(f'Failed to connect to MQTT broker: {rc}')


def on_message(client, userdata, msg):
	'''
	Callback for when a message is received from the server.
	
	:param client: The client instance for this callback
	:param userdata: The private user data as set in Client() or user_data_set()
	:param msg: An instance of MQTTMessage. This is a
	'''
	
	service_envelope = mqtt_pb2.ServiceEnvelope()

	try:
		service_envelope.ParseFromString(msg.payload)
		# print(service_envelope)
		message_packet = service_envelope.packet
		# print(message_packet)
	except Exception as e:
		logging.error(f'Failed to parse message: {str(e)}')
		return

	if message_packet.HasField('encrypted') and not message_packet.HasField('decoded'):
		decode_encrypted(message_packet)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Mesh MQTT')
	parser.add_argument('--broker', default='mqtt.meshtastic.org', help='MQTT broker address')
	parser.add_argument('--port', default=1883, type=int, help='MQTT broker port')
	parser.add_argument('--root', default='msh/US/2/c', help='Root topic')
	parser.add_argument('--tls', action='store_true', help='Enable TLS/SSL')
	parser.add_argument('--username', default='meshdev', help='MQTT username')
	parser.add_argument('--password', default='large4cats', help='MQTT password')
	parser.add_argument('--key', default='AQ==', help='Encryption key')
	args = parser.parse_args()

    # Ensure the key is padded and formatted correctly
	padded_key   = args.key.ljust(len(args.key) + ((4 - (len(args.key) % 4)) % 4), '=')
	replaced_key = padded_key.replace('-', '+').replace('_', '/')
	key          = replaced_key

	broadcast_id = 4294967295

	# client = mqtt.Client(client_id='', clean_session=True, userdata=None)
	client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
	client.on_connect = on_connect
	client.username_pw_set(username=args.username, password=args.password)
	client.connect(args.broker, args.port, 60)
	client.on_message = on_message
	client.subscribe(args.root, 0)

	while client.loop() == 0:
		pass
