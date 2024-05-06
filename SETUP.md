# Setup Hardware

It is recommended that you provision your hardware using the serial interface over USB by using the [Meshtastic CLI Tool](https://pypi.org/project/meshtastic/). This is very specific because currently, at the time of writing this repository, changes made via the [web interface](https://client.meshtastic.org) do not work sometimes. When you "save" your settings, the device will reboot with the old settings still. I have had zero issues making changes over serial with the CLI interface.

- `pip install meshtastic` to install the CLI tool
- Plug in your device *(Make sure the USB cable you are using allows data transfer & not just power)*
- Run the commands below *(Each command will make the device reboot after setting it)*

###### NAME
```
meshtastic --set-owner 'CHANGEME' --set-owner-short 'CHNG'
```

**Note:** Short name can only be 4 alphanumeric characters.

###### LORA
```
meshtastic --set lora.region US 
```

###### GPS
```
meshtastic --set position.gps_enabled true
```

or for a fixed position...

```
meshtastic --set position.fixed_position true --setlat 37.8651 --setlon -119.5383
```

###### POWER
```
meshtastic --set power.is_power_saving false
```

###### CHANNEL
```
meshtastic --ch-set name "SUPERNETS" --ch-set psk "CHANGEME" --ch-set uplink_enabled true --ch-set downlink_enabled true --ch-index 0
```

###### WIFI
```
meshtastic --set network.wifi_enabled true --set network.wifi_ssid "CHANGEME" --set network.wifi_psk "CHANGEME"
```

###### MQTT
```
meshtastic --set mqtt.enabled true --set mqtt.address changeme --set mqtt.username changeme --set mqtt.password changeme --set mqtt.encryption_enabled true --set mqtt.tls_enabled false --set mqtt.root msh --set mqtt.map_reporting_enabled true --set mqtt.json_enabled true
```

###### BLUETOOTH
```
meshtastic --set bluetooth.enabled true
```

**Note:** Only enable this on devices are not using Wifi *(mobile devices)* because with ESP32 chips, I don't think Wifi & Bluetooth can function side-by-side together.
