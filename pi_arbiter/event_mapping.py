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


# reed contacts directly hooked up into the arbiter
class ArbiterIO(IntEnum):
    pcfIn = 4   # 0x3C
    entrance = 1 << 0
    apartmentDoor = 1 << 1


class LightIO(IntEnum):
    pcfOut = 0  # 0x38
    service_enable = 1
    gameStart = 2
    gameEndTrigger = 3
    hallwayStart = 4
    hallwayOff = 5
    hallwayOn = 6
    hallwayDimmed = 7
    apartmentEnter = 8
    chimneyOverride = 9
    mcBoot = 10
    waterUV = 11
    gamereset = 12

    pcfIn = 3   # 0x3B
    chinmeySolved = 128


class FuseIo(IntEnum):
    pcfOut = 1  # 0x39
    startGame = 1 << 0
    mcOpened = 1 << 1

    pcfIn = 3   # 0x3B
    mcBoot = 1
    lightOff = 2
    lightOn = 4
    doorOpen = 8


class WaterIO(IntEnum):
    pcfIn = 4   # 0x39 binary
    uvActive = 1 << 2

class BreakoutIO(IntEnum):
    pcfIn = 5   # 0x3D
    solved = 1

    pcfOut = 2  # 0x3A
    roomReset = 1
    mcBoot = 2
    setSolved = 3


binary_pcfs = [FuseIo.pcfIn, FuseIo.pcfIn]


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

    "game_reset": {
        pcf_out_add: [BreakoutIO.pcfOut],
        pcf_out: [BreakoutIO.roomReset]
    },

    "game_start": {
        pcf_in_add: ArbiterIO.pcfIn,
        pcf_in: ArbiterIO.apartmentDoor,
        pcf_out_add: [LightIO.pcfOut, FuseIo.pcfOut],
        pcf_out: [LightIO.gameStart, FuseIo.startGame],
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
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.lightOff,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOff],
    },

    "hallway_on": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.lightOn,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOn]
    },

    "hallway_dimmed": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayDimmed],
    },

    "appartment_enter": {
        pcf_in_add: ArbiterIO.pcfIn,
        pcf_in: ArbiterIO.apartmentDoor,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.apartmentEnter],
    },

    # opening of the chinmey, fades in and out to set its fokus
    "chimney_opening": {
        pcf_in_add: LightIO.pcfIn,
        pcf_in: LightIO.chinmeySolved,
        pcf_out_add: [LightIO.pcfIn, FuseIo.pcfOut],
        pcf_out: [LightIO.chimneyOverride, FuseIo.mcOpened],
    },


    "water_solved": {
        pcf_in_add: WaterIO.pcfIn,
        pcf_in: WaterIO.uvActive,
    },

    "fusebox_doorOpened": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.doorOpen
    },

    # boots up PCs from the floppy riddle, lights up the MC
    "fusebox_bootMC": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.mcBoot,
        pcf_out_add: [BreakoutIO.pcfOut],
        pcf_out: [BreakoutIO.mcBoot],
    },

    "breakout_solved": {
        pcf_in_add: BreakoutIO.pcfIn,
        pcf_in: BreakoutIO.solved,
        pcf_out_add: [BreakoutIO.pcfOut],
        pcf_out: [BreakoutIO.setSolved],
    },
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






