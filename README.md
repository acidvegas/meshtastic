# Meshtastic Utilities

This repository serves as a collection of resources created in my journey to learn & utilize [LoRa](https://en.wikipedia.org/wiki/LoRa) based communications with [Meshtastic](https://meshtastic.org).

The goal here is to create simple & clean modules to interface with the hardware in a way that can be used to expand the possibilities of the devices capabilities.

![](.screens/htpdeck.png)

## Documentation
- [Hardware Options](./docs/HARDWARE.md)
- [Setup Hardware](./SETUP.md)
- [Setup a T-Deck](./docs/T-DECK.md)
- [Firmware Hacks & Customization](./docs/FIRMWARE.md)
- [MQTT Notes](./docs/MQTT.md)

## Code
- [Meshtastic Serial/TCP Interface](./meshapi.py)
- [Meshtastic MQTT Interface](./meshmqtt.py)
- [Meshtastic IRC Relay / Bridge](./meshirc.py)

## Bugs & Issues
- Devices must have Wifi turned off when going mobile. Upon leaving my house with WiFi still enabled, the UI & connection was EXTREMELY laggy & poor. Couldn't even type well...
- Devices using a MQTT with TLS will reboot loop.
- A fix for the reboot loop is simply disabling MQTT over serial with `meshtastic --set mqtt.tls_enabled false`
- Enabling JSON with MQTT causes messages to not be encrypted in the MQTT server..

## Roadmap
- Asyncronous meshtastic interface
- Documentation on MQTT bridging for high availability
- Bridge for IRC to allow channel messages to relay over Meshtastic & all Meshtastic events to relay into IRC. *(IRC to Meshtastic will require a command like `!mesh <message here>` to avoid overloading the traffic over LoRa)*

___

###### Mirrors for this repository: [acid.vegas](https://git.acid.vegas/meshtastic) • [SuperNETs](https://git.supernets.org/acidvegas/meshtastic) • [GitHub](https://github.com/acidvegas/meshtastic) • [GitLab](https://gitlab.com/acidvegas/meshtastic) • [Codeberg](https://codeberg.org/acidvegas/meshtastic)