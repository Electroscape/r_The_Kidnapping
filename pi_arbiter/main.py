# @author Martin Pek (martin.pek@web.de)

import time

import json
import socketio
# not a fan of * impports ... amybe we can make classes

from event_mapping import *
import logging
from ArbiterIO import ArbiterIO, CooldownHandler
# standard Python would be python-socketIo
from time import sleep, thread_time

from communication.Simple_Socket import TESocketServer, SocketClient
from pathlib import Path
from datetime import datetime as dt, timedelta

time_start = None

IO = ArbiterIO()

'''
@TODO: 
    * 🔲 test
    * 🔲 uncomment TV trigger?
    * ✅ 
'''

sio = socketio.Client()
cooldowns = CooldownHandler()
floppy_sock_server = None
tv_sock_server = None

gpio_thread = None
# used to prevent multiple boots
connected = False


reset_gpios_dicts = {}
reset_delta = timedelta(seconds=3)
# used for delayed events
event_shedule = {}
cooldown_time = 0.5

now = dt.now()
log_name = now.strftime("eventlogs/Arbiter events %m_%d_%Y  %H_%M_%S.log")
logging.basicConfig(filename=log_name, level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s : %(message)s')


def get_cfg():
    try:
        with open('config.json') as json_file:
            return json.loads(json_file.read())
    except ValueError as e:
        print('failure to read config.json')
        print(e)
        exit()


@sio.event
def connect():
    print("Connected to Server!")


def get_event_value(event_key, event_value):
    if event_value is None:
        try:
            event_value = event_map[event_key]
        except KeyError:
            print(f"handle_event received invalid key: {event_key}")
    return event_value


def trigger_event(event_key, event_value=None):
    event_value = get_event_value(event_key, event_value)
    if event_value is None:
        return

    print(f"triggered event {event_key}")

    # IO pins
    try:
        # @todo: type casting here?
        pcf_no = event_value[pcf_out_add]
        values = event_value[pcf_out]
        print(f"setting outputs: PCF={pcf_no} Value={values}")

        pcf_value_dict = {}
        # edit here
        for index in range(min(len(values), len(pcf_no))):
            pcf = pcf_no[index]
            pcf_value_dict[pcf] = pcf_value_dict.get(pcf, 0) + values[index]
            reset_gpios_dicts.update({pcf_no[index]: dt.now() + reset_delta})
        for pcf, value in pcf_value_dict.items():
            IO.write_pcf(pcf, value)
    except KeyError as err:
        print(err)
        pass
    try:
        handle_event_fe(event_value, event_key)
    except socketio.exceptions as exp:
        logging.debug(f"error with sending message to FE: {exp}")
    queued_event = event_value.get(event_next_qeued, False)
    if queued_event:
        handle_event(queued_event)


def handle_event(event_key, event_value=None, frontend_override=False):
    event_value = get_event_value(event_key, event_value)
    if event_value is None:
        return

    try:
        if not event_value.get(event_condition, lambda: True)() and not frontend_override:
            # print(f"conditions not fullfilled {event_key}")
            return
        event_value.get(event_script, lambda *args: 'Invalid')(event_key, floppy_sock_server, tv_sock_server)
    except TypeError as err:
        print(f"Error with event fnc/condition {err}")

    if event_value.get(event_delay, 0):
        event_shedule.update({event_key: dt.now() + timedelta(seconds=event_value.get(event_delay, 0))})
        return

    trigger_event(event_key, event_value)


def handle_event_fe(event_value, event_key):
    # Otherwise we crash
    if not sio.connected:
        return
    cb_dict = event_value.get(fe_cb, False)
    if not cb_dict:
        # This way any event can be monitored on the server
        sio.emit("events", {"username": "server", "message": event_key})
        return
    cb_tgt = cb_dict.get(fe_cb_tgt, False)
    cb_cmb = cb_dict.get(fe_cb_cmd, False)

    if not cb_cmb or not cb_tgt:
        return
    cb_msg = cb_dict.get(fe_cb_msg, "")
    print(f"sio emitting: {cb_tgt} {cb_cmb} {cb_msg}\n\n")
    sio.emit("events", {"username": cb_tgt, "cmd": cb_cmb, "message": cb_msg})
    

'''
@sio.on('*')
def catch_all(event, sid, *args):
    print(f'catch_all(event={event}, sid={sid}, args={args})')
'''


@sio.on("trigger")
def handle_fe(data):
    print(f"triggerdate{data}")
    print("\n")
    try:
        if not data.get('username') == 'arb':
            return False
    except KeyError:
        return False

    for key, event in event_map.items():
        try:
            # print("\n")
            # event_name = event[fe_event]
            cmd = event.get(trigger_cmd, False)
            if not cmd or cmd != data.get('cmd'):
                continue
            msg = event.get(trigger_msg, False)
            if msg and msg != data.get("message"):
                continue
            handle_event(key, frontend_override=True)
        except KeyError:
            pass


def handle_pcf_input(input_pcf, value):

    # local version so we can have one PCF input potentially trigger multiple events
    temporary_cooldowns = set()

    rejected = True

    for event_key, event_dict in event_map.items():

        try:
            if event_dict.get(pcf_in_add) != input_pcf:
                continue
            event_pcf_value = event_dict.get(pcf_in, -1)

            # checks if all pins to form the value of that event are present on the inputs
            # this way its possible mix and match multiple inputs as single pin inputs and binary
            if input_pcf in binary_pcfs:
                if event_pcf_value == value:
                    # @TODO: consider simply using the eventkeys
                    if not cooldowns.is_input_on_cooldown(input_pcf, event_pcf_value):
                        temporary_cooldowns.add((input_pcf, event_pcf_value, thread_time() + cooldown_time))
                        handle_event(event_key)
                        rejected = False
            else:
                if event_pcf_value & value == event_pcf_value:
                    # @TODO: consider simply using the eventkeys
                    if not cooldowns.is_input_on_cooldown(input_pcf, event_pcf_value):
                        temporary_cooldowns.add((input_pcf, event_pcf_value, thread_time() + cooldown_time))
                        handle_event(event_key)
                        rejected = False

        except KeyError:
            continue

    if rejected:
        pass
        # print(f"\n\nInvalid PCF input\n PCFNo {input_pcf} value {value}\n\n")
    cooldowns.cooldowns.update(temporary_cooldowns)


def handle_pcf_inputs(active_inputs):
    for active in active_inputs:
        handle_pcf_input(*active)


# only applies to non binary pin based values
def handle_inverted_events(active_inputs):
    for event_key, event_value in inverted_events.items():
        # print(f"\n chcecking {event_key}:")
        if inverted_triggered(event_value, active_inputs):
            # print(f"attempting event {event_key}")
            handle_event(event_key, event_value)
        # else:
            # print(f"{event_key} not triggered")


def inverted_triggered(event_value, active_inputs):
    pcf_addr = event_value.get(pcf_in_add, -1)
    pcf_value = event_value.get(pcf_in, -1)
    for pcf_input in active_inputs:
        # print(pcf_input)
        if pcf_input[0] == pcf_addr:
            # print(f"{pcf_value} compared {pcf_input[1]}")
            # print(pcf_value & pcf_input[1])
            if pcf_value & pcf_input[1] > 0:
                return False
    return True


def reset_gpios():
    # print(reset_gpios_dicts)
    remove_keys = []
    for pcf_no, reset_time in reset_gpios_dicts.items():
        if reset_time < dt.now():
            # print(f"resetting gpio {pcf_no} {reset_time}")
            IO.write_pcf(pcf_no, 0)
            remove_keys.append(pcf_no)
    for key in remove_keys:
        reset_gpios_dicts.pop(key)


def handle_event_shedule():
    remove_keys = []
    for event_name, event_time in event_shedule.items():
        if event_time < dt.now():
            remove_keys.append(event_name)
            trigger_event(event_name)
    for key in remove_keys:
        event_shedule.pop(key)


def connect():
    server_add = cfg.get("terminal_server_add", 0)
    if not server_add:
        exit("missing socketio server")
    while True:
        try:
            sio.connect(server_add)
            return True
        except socketio.exceptions.ConnectionError as exc:
            print(f'Caught exception socket.error : {exc}')
            sleep(1)


def main():
    while True:
        active_inputs = IO.get_inputs()
        handle_pcf_inputs(active_inputs=active_inputs)
        handle_inverted_events(active_inputs)
        reset_gpios()
        handle_event_shedule()


def init_socket(settings):
    print("Initialising Sockets")
    global tv_sock_server
    try:
        tv_port = settings["tv_server"]["port"]
        tv_sock_server = TESocketServer(tv_port)
        print(f"TV socket server is active on port {tv_port}")
    except KeyError:
        print("KeyError: tv_sock_server")

    global floppy_sock_server
    try:
        client_cfg = settings["socket_client"]
        server_add = client_cfg["server_add"]
        port = client_cfg["port"]
        floppy_sock_server = SocketClient(server_add, port)
        print(f"starting socketclient with {server_add} as server")
        return  ## do we really return here?
    except KeyError:
        pass
    try:
        client_cfg = settings["socket_server"]
        port = client_cfg["port"]
        floppy_sock_server = TESocketServer(port)  ## do we override the same variable?
        print(f"starting socketServer on port {port}")
        return
    except KeyError:
        pass



if __name__ == '__main__':
    cfg = get_cfg()
    init_socket(cfg)
    connected = connect()

    print("\n\n=== Arbiter setup complete! ===\n\n")

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        sio.disconnect()
