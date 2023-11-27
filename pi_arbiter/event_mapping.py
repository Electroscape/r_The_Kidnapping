import requests
import subprocess
from enum import IntEnum
import re

'''
@TODO: 
    * 🔲 test
    * 🔲 uncomment TV trigger?
    * ✅ 
    * 🔲 list directly connected reeds and TYPE of NC/NO required
'''


# these are the pcf addresses, first 3 are Arbiter -> Brain as outputs
# last 3 are Brain -> Arbiter inputs

# for rev 0.2 and onwards
# [0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]

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


class LightIO(IntEnum):
    pcfOut = 0  # 0x38
    service_enable = 1
    gameStart = 2
    gameEndTrigger = 3
    hallwayStart = 4
    hallwayOff = 5
    hallwayOn = 6
    hallwayDimmed = 6
    apartmentEnter = 7
    apartmentDim = 8

    pcfIn = 3   # 0x3B
    chinmeySolved = 1 << 7


class FuseIO(IntEnum):
    pcfOut = 1  # 0x39
    startGame = 1 << 0
    mcOpened = 1 << 1

    pcfIn = 3   # 0x3B
    mcBoot = 1
    lightOff = 2
    lightOn = 3


binary_pcfs = []

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
        pcf_out_add: [0],
        pcf_out: [0],
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "boot"
        },
        event_script: call_video,
        event_next_qeued: "self_check_q1"
    },

    "service_enable": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.service_enable],
    },

    "game_start": {
        pcf_out_add: [LightIO.pcfOut, fuseIO.pcfOut],
        pcf_out: [LightIO.gameStart, fuseIO.startGame],
    },

    "game_endtrigger": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.gameEndTrigger],
    },

    "hallway_start": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayStart],
    },

    "hallway_off": {
        pcf_in_add: [fuseIO.pcfIn],
        pcf_in: [fuseIO.lightOff],
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOff],
    },

    "hallway_on": {
        pcf_in_add: [fuseIO.pcfIn],
        pcf_in: [fuseIO.lightOn],
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOn]
    },

    "hallway_dimmed": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayDimmed],
    },

    "appartment_enter": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.apartmentEnter],
    },

    "appartment_dim": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.apartmentDim],
    },

    # opening of the chinmey, fades in and out to set its fokus
    "chimney_opening": {
        pcf_out_add: [LightIO.pcfIn, fuseIO.pcfOut],
        pcf_out: [LightIO.chinmeySolved, fuseIO.mcOpened],
    },


    "water_solved": {},

    "fusebox_solvedHallway": {},
    # boots up PCs from the floppy riddle, lights up the MC
    "fusebox_bootMC": {
        pcf_in_add: [fuseIO.pcfIn],
        pcf_in: [fuseIO.mcBoot],
    },

    "breakout_boot": {},
    "breakout_solved": {},
    "breakout_setSolved": {},

    "light_hallwayDimmed": {},
    "light_hallwayOff": {},
    # triggered when the
    "light_hallwayStart": {},

    # opened by reed of the appartment door, 1 minute fadein
    "light_enteringFlat": {},
}

def setup_default_callbacks():
    for event_key in event_map.keys():
        event_data = event_map[event_key]

        if not (event_data.get(trigger_msg, False) and event_data.get(trigger_cmd, False)):
            triggers = re.split("_", event_key)
            if len(triggers) == 2:
                event_map[event_key][trigger_cmd] = triggers[0]
                event_map[event_key][trigger_msg] = triggers[1]

setup_default_callbacks()


# Only can be applied to non binary pinbased inputs
inverted_events = {
}






