#!/usr/bin/env python
# Meshtastic MQTT Interface - Developed by Acidvegas in Python (https://git.acid.vegas/meshtastic)

import base64
import random

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends           import default_backend
except ImportError:
    raise ImportError('cryptography library not found (pip install cryptography)')

try:
    from meshtastic import mesh_pb2, mqtt_pb2, portnums_pb2, telemetry_pb2
except ImportError:
    raise ImportError('meshtastic library not found (pip install meshtastic)')

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError('paho-mqtt library not found (pip install paho-mqtt)')


# MQTT Configuration
MQTT_BROKER     = 'localhost'
MQTT_PORT       = 1883
MQTT_USERNAME   = 'username'
MQTT_PASSWORD   = 'password'
MQTT_ROOT_TOPIC = 'msh/US/2/c/'
CHANNEL_KEY     = 'channel_key'


def on_connect(client, userdata, flags, rc, properties):
    '''
    Callback for when the client receives a CONNACK response from the server.
    
    :param client:     The client instance for this callback
    :param userdata:   The private user data as set in Client() or user_data_set()
    :param flags:      Response flags sent by the broker
    :param rc:         The connection result
    :param properties: The properties returned by the broker
    '''

    if rc == 0:
        print('Connected to MQTT broker')

    else:
        print(f"Failed to connect to MQTT broker with result code {str(rc)}")


def on_message(client, userdata, msg):
    '''
    Callback for when a PUBLISH message is received from the server.
    
    :param client:    The client instance for this callback
    :param userdata:  The private user data as set in Client() or user_data_set()
    :param msg:       An instance of MQTTMessage. This is a class with members topic, payload, qos, retain.
    '''

    service_envelope = mqtt_pb2.ServiceEnvelope()

    try:
        service_envelope.ParseFromString(msg.payload)
        print(service_envelope)

        message_packet = service_envelope.packet
        print(message_packet)

    except Exception as e:
        print(f'error on message: {e}')

    else:
        if message_packet.HasField('encrypted') and not message_packet.HasField('decoded'): # Do we need to check for both?
            pass # Need to finish this



if __name__ == '__main__':
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.on_message = on_message
    client.subscribe(MQTT_ROOT_TOPIC, 0) # This is the topic that the Meshtastic device is publishing to

    # Keep-alive loop
    while client.loop() == 0:
        pass