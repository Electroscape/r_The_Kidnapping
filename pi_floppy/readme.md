# Guidelines of installation

use a GUI RPI image

## pre-installation

1. connect rfid on i2c pin on rpi
2. from `sudo raspi-config` Enable i2c

## installation

1. run `bash install.sh`
2. at end of  `sudo nano /etc/nfc/libnfc.conf` add

    ```bash
    device.name = "PN532 over I2C"
    device.connstring = "pn532_i2c:/dev/i2c-1"
    ```

3. run `i2cdetect -y 1` to assure i2c sensor is detected corretly. Default address is 0x24
4. So important: **disable hardware acceleration in chromium**
5. To hide the mouse cursor edit `sudo nano /etc/lightdm/lightdm.conf` You must add this line after [Seat*] declaration `xserver-command=X -nocursor`

## Possible installation problems

import board
ModuleNotFoundError: No module named 'board'

sudo python3 -m pip install --force-reinstall adafruit-blinka

## Configuration

1. floppy can work in offline mode without connection to a server, however, to be connected to a server change the line in `floppy.py` to the correct address e.g. `server_ip = "http://spi-sv-floppy:5500"`
2. In `run.sh` change the ip of the kiosk display.
3. Update crontab to execute `run.sh` at reboot.
