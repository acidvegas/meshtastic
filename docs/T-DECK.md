# Meshtastic on a T-Deck

![](.screens/htpdeck.png)

## Parts
- [T-Deck](https://www.lilygo.cc/products/t-deck)
- [Case](https://www.printables.com/model/741124-lilygo-t-deck-case)
    - You can 3D print it yourself, or you can buy one on Etsy from the link above.
- [Antenna](https://www.amazon.com/Connector-868-915MHz-Lora32u4-Internet-WIshiOT/dp/B07LCKNN4H)
    - The T-Deck has an I-PEX connection point for antennas. I used an I-PEX-to-SMA adapter so I could screw on a little 2dbi antenna.
- [GPS]https://www.amazon.com/Teyleten-Robot-Dual-Mode-Positioning-Replacement/dp/B09LQDG1HY)
    - There may be a better 15mm option for the case above...this is just what I used.
- [Battery](https://www.amazon.com/AKZYTUE-5000mAh-Battery-Rechargeable-Connector/dp/B07TXJ5XXZ/)
    - The battery you get depends on the size of the case you order. Do your measurements, contact me if you need help.

## GPS Installation
The T-Deck has a grove connector for the GPS, but for using this inside of a case, I decided to remove the connector and solder the GPS directly to the board.

###### Soldering
You will see VCC, GND, RX & TX points on both the T-Deck & the GPS. Solder wires to match these points, but switch RX & TX. So do VCC to VCC, GND to GND, and then ensure that RX is soldered to TX, and TX is soldered to RX.

###### WARNING
Be careful taking off the grove! Snip the front connnection points and then use a soldering iron to loosen the metal on the 4 back side connection points. You can VERY easily pull the solder pads right off if you just try to rip the grove connector off without loosening the solder points. If you pull off a solder pad, you're pretty much boned on having a GPS module. This has happened to ALOT of people with these things.

![](.screens/solder_pads_lol.png)

*Above: Picture of solder pads accidentally pulled off lol...*

## Flashing
###### **WARNING:** Do not power on the device until the antenna is plugged in! Even to flash the firmware, or for testing, make sure your antenna is plugged in or you can fry the radio!

Simply plug in the T-Deck via USB and connect to a computer, then visit the [Meshtastic Web Flasher](https://flasher.meshtastic.org) and select your hardware & firmware version. Your device should show up as a serial device on /dev/ttyUSB0 or /dev/ttyAMC0. If you do not see your device, try adding your user to the dialout group. See [SETUP.md](./SETUP.md) for information on how to setup the device once it is flashed with Meshtastic.