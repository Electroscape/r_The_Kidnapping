# POD83 Terminals

This repo contains three flask apps:

- server.py
- ter1.py
- ter2.py

## RPi Setup

Install a new RPi image (Desktop with recommended pre-installed packages) using RPi imager. It should contain python3.9
which is the minimum version to run the app. Make sure to:

- `python --version` is at least python 3.9
- Change the hostname to an informative one
- Give it a static IP
- disable password manager from chromium
- add zoom block extension to chromium https://chrome.google.com/webstore/detail/zoom-block/jmomepcgehgfoimapeoinphcloinjfpb

Screen blanking needs to be disabled: \
`sudo raspi-config` -> display options -> screen blanking

### RPI setup from scratch

1. Download and install [RPi-Imager](https://www.raspberrypi.com/software/)  on your PC

2. From the settings
    1. Enable `ssh`
    2. change `hostname`
    3. set `password`

3. Card in Pi -> boot -> login via ssh

4. Set fixed IP address by `sudo nano /etc/dhcpcd.conf`:

   ```bash
   interface eth0
   static ip_address=192.168.xxx.yyy/24
   static routers=192.168.xxx.zzz
   static domain_name_servers=192.168.xxx.zzz 8.8.8.8
   ```

5. `wget https://raw.githubusercontent.com/Electroscape/Tools/master/setup_repo.sh`

6. `sudo chmod +x setup_repo.sh`

7. `./setup_repo.sh <your_username>  <username@email.com>`

8. `cd ~/Electroscape/r_POD83/m_terminal` !! currently `m_terminal` only exists on `ter_develop` branch. Make sure to
   "checkout" the correct branch by `git checkout ter-develop` until there is a release in the `main` branch

9. `bash install.sh`

10. `bash run.sh`

project contains shellscripts, those can be made executable with `chmod +x myfile`

## Common Issues

### Socket-IO

ImportError: No module named socketio

```
python -m pip uninstall socketio
python -m pip uninstall python-socketio
python -m pip install python-socketio 
```

## For development on a PC

The project contains the `launch.json` for `vscode IDE`. You can debug and start, stop and watch each port individually.
However, the `jinja` snippets are not recognised, so it is recommended to use `pyCharm IDE` in that case.

## notes

- Flask blocks cross-origin requests unless it is manually allowed. In `static/json/server-config.json` in the `"ip"`
  dict,
  add all possible IPs that could communicate in the setup.
- `ter1.py` and `ter2.py` can only work if the `server.py` is running and reachable. Get the IP which is the server
  running on and update the variable `server_ip` in the terminal script.
- In `ter1` the `media` page can only be loaded if there is content in `static/media` folder.
- The `kiosk.py` script is irrelevant to the setup. It is used to add tabs to display both terminals and the server in one webpage in
  the kiosk mode. Simply, change `ips` dict in `kiosk.py` to create your webpage with tabs (easier to monitor several pages at the same time).

## Useful Commands

- To run flask app use the command: `FLASK_APP=server.py FLASK_DEBUG=true flask run --host 0.0.0.0 --port 5500 &`
  replace script name and the port accordingly.
- To display the app in kiosk mode use the
  command: `DISPLAY=:0 /usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk 192.168.xxx.yyy:port &`
