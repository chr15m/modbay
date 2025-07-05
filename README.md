Tracker module live performance device.

This application is designed for performing live with tracker modules on a handheld device.
The hardware is a Gpi case for the Raspberry Pi zero.

To run the app on the device: `./main.sh`

To run the app in dev mode on a laptop: `./dev.sh`

Tested on: Python 3.7.17

![Photograph of modbay running on hardware](./modbay.png)

# Set high priority realtime audio

```
sudo cat<<EOT > /etc/security/limits.d/audio.conf
@audio   -  rtprio     95
@audio   -  memlock    unlimited
EOT
```

# Dependencies

 * [Python 3](https://python.org)
 * [`xmp`](https://github.com/libxmp/libxmp)
 * [`pd`](https://puredata.info/)

`sudo apt install xmp python3 puredata`

# RetroPie launcher

To run this application automatically on boot, you can use the `retropie-launcher.sh` script.
This script is designed to be called from RetroPie's `autostart.sh` file.

Assuming `retropie-launcher.sh` is located in `/home/pi/modbay`, you can edit `/opt/retropie/configs/all/autostart.sh` on your device to automatically start `modbay`.

To run the application once and then exit to the command line (or Emulation Station if configured), change `autostart.sh` to:

```bash
/home/pi/modbay/retropie-launcher.sh
```

If you want the application to restart automatically if it exits (for a kiosk-style setup), you can wrap the command in a `while` loop:

```bash
while true; do
  /home/pi/modbay/retropie-launcher.sh
done
```
