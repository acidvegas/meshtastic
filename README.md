# Meshtastic Utilities
> Experiments with Meshtastic, MQTT, Lora, & more....

## WORK-IN-PROGRESS

Here I will be just throw up random bits of code I write as I experiment more with these Meshtastic devices.

Currently using a [Lilygo T-Deck](https://www.lilygo.cc/products/t-deck) & a [Heltec Lora 32 v3](https://heltec.org/project/wifi-lora-32-v3/) for testing.

I am waiting on a [Lilygo T-Beam](https://www.lilygo.cc/products/t-beam-v1-1-esp32-lora-module) & a [RAK Wireless 4631](https://store.rakwireless.com/products/wisblock-core-modules?variant=42440631419078) to arrive for expanding my network & conducting more testing.

Reading device packets over serial or TCP allows you to see the decoded data easily & fast. I have plans to add MQTT interfacing to this repository, but note that this requires you to decrypt incomming packet payloads using the channels PSK. We will get to that in the future.

The goal is to experiment with the possibilities of Python as a means of interfacing with a Meshtastic device, playing with basic I/O operations, etc. My first project is going to be a relay for IRC & Meshtastic to communicate.

## Links
- [T-Deck 3D Printed Case](https://www.printables.com/model/741124-lilygo-t-deck-case)

# Notes
- T-Deck is must have Wifi turned off when going mobiel *(Unstable UI & connection)*
- T-Deck using a custom MQTT with TLS & auth will cause a reboot loop *(Need to fix this ASAP)*
- Add support for interfacing over MQTT with decryption support
- `on_node` event is called **AS** we are defining the interface, so using `self.interface` in that callback will error

## Updates
- Threw in an IRC skeleton where the serial controller will interface with. Will have to consider how handle asyncronous comms over serial...
- Working reconnection on disconnection!
- Most events are handled and outputted to stdout, debugging and testing finished
___

###### Mirrors for this repository: [acid.vegas](https://git.acid.vegas/meshtastic) • [SuperNETs](https://git.supernets.org/acidvegas/meshtastic) • [GitHub](https://github.com/acidvegas/meshtastic) • [GitLab](https://gitlab.com/acidvegas/meshtastic) • [Codeberg](https://codeberg.org/acidvegas/meshtastic)