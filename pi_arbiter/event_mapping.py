import requests
import subprocess
from enum import IntEnum



laserlock_out_pcf = 0

pcf_in = "pcf_in"
# if a specific pin must be set to high in order to trigger, only works on non-binary
pcf_in_add = "pcf_in_add"
pcf_out = "pcf_out"
pcf_out_add = "pcf_out_add"

# event triggered from FE
trigger_cmd = "trigger_cmd"
# may not always be required
trigger_msg = "trigger_msg"
# event triggering FE

fe_cb = "fe_cb"
fe_cb_tgt = "tgt"
fe_cb_cmd = "cmd"
fe_cb_msg = "msg"

event_script = "script"
event_condition = "condition"
event_delay = "delay"
event_next_qeued = "event_next"


class AirlockOut(IntEnum):
    david_end = 1 << 7
    rachel_announce = 1 << 6
    rachel_end = 1 << 5

class LockerIn(IntEnum):
    serviceEnable = 1 << 4
    serviceDisable = 1 << 5


binary_pcfs = [airlock_in_pcf, laserlock_in_pcf]

class States:
    def __init__(self):
        self.example = False


states = States()




def call_video(event_key, nw_sock):
    nw_sock.transmit(event_key)


event_map = {
    "self_check": {
        trigger_cmd: "self",
        trigger_msg: "check",
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [0],
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "boot"
        },
        event_script: call_video,
        event_next_qeued: "self_check_q1"
    },
}


# Only can be applied to non binary pinbased inputs
inverted_events = {
}






