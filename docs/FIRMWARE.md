# Meshtastic Firmware Hacks

## Prerequisite
- Download & install [PlatformIO](https://platformio.org/platformio-ide)

- `git clone https://github.com/meshtastic/firmware.git`

- `cd firmware && git submodule update --init`

## Customization
###### Custom Boot Logo
- Use [XMB Viewer](https://windows87.github.io/xbm-viewer-converter/) to convert an image to XMB

- The data from this goes in `firmware/src/graphics/img/icon.xbm`

You can use the provided [icon.xbm](../assets/icon.xbm) for a rad GTA:SA fist to show up on boot.

###### Custom boot message
- Navigate to `firmware/src/graphics/Screen.cpp`

- Find & replace `const char *title = "meshtastic.org";` with your custom message.

###### Custom screen color
 - Navigate to `src/graphics/TFTDisplay.cpp`

 - Find & replace `#define TFT_MESH COLOR565(0xFF, 0x00, 0x00)` with your custom color. *(The one shown here is for RED mode >:))*

 ###### Custom alert sound (for T-Deck & devices with a buzzer)
 - From the mobile app, click the 3 dots on the top right, and select `Radio configuration`
 - Under `Module configuration`, select `External Notification`
- Scroll down & you will see a `Ringtone` option that takes [RTTTL](https://en.wikipedia.org/wiki/Ring_Tone_Text_Transfer_Language) formatted tones.

As far as I know, at the time of writing this, the only way to change the Ringtone is from the App. While this is not a "firmware" related thing, I included it in this file because it was difficult to find this setting...

 ## Compile & flash firmware
 - Select `PlatformIO: Pick Project Environment` & select your board.
 - Run `PLatformIO: Build` to compile the firmware.
 - Place device in DFU mode & plug in to the computer
 - Do `PlatformIO: Upload` to send the firmware to the device
 - Press the RESET button or reboot your device.

 See [here](https://meshtastic.org/docs/development/firmware/build/) for more information building & flashing custom firmware.