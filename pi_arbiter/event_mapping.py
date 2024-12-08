import requests
import subprocess
from enum import IntEnum
import re
import time


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
    gameSolved = 3
    hallwayStart = 4
    hallwayOff = 5
    hallwayOn = 6
    hallwayDimmed = 7
    apartmentEnter = 8
    chimneyOverride = 9
    mcBoot = 10
    waterUV = 11
    gameReset = 12
    gameOver = 13

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
    roomReset = 1 << 5
    mcBoot = 1 << 6
    setSolved = 1 << 7


class PowerIO(IntEnum):
    pcfOut = 2  # 0x3A
    roomReset = 1
    emporeOn = 2
    emporeOff = 3
    livingOn = 4
    livingOff = 5
    raum2On = 6
    raum2Off = 7
    serviceOn = 8
    serviceOff = 9
    chimneyOpening = 10


# binary_pcfs = [FuseIo.pcfIn, ArbiterIO.pcfIn]
binary_pcfs = []


class GameStatus:
    def __init__(self):
        self.example = False
        self.hasStarted = False
        self.gameLive = False   # suppress in case of other light effects? only for the green solved
        self.hallway_started = False
        self.appartmentEntered = False


game_states = GameStatus()

def wait_for_lightEffekt(*args):
    time.sleep(20)
def wait_for_lightEffekt2(*args):
    time.sleep(15)
def wait_for_chimney(*args):
    time.sleep(13)


def set_live(_, nw_sock):
    game_states.gameLive = True
    game_states.hasStarted = False
    game_states.appartmentEntered = False
    game_states.hallway_started = False
    nw_sock.transmit("reset")


def is_game_started(*args):
    return game_states.hasStarted

def can_start_hallway(*args):
    if not game_states.hasStarted:
        return False
    if not game_states.hallway_started:
        game_states.hallway_started = True
        return game_states.hallway_started
    else:
        return False



def can_enter_appartment(*args):
    if game_states.hasStarted:
        if not game_states.appartmentEntered:
            game_states.appartmentEntered = True
            return game_states.appartmentEntered
    return False


def is_game_live(*args):
    return game_states.gameLive


def  start_game_condition(*args):
    if game_states.gameLive:
        if not game_states.hasStarted:
            game_states.hasStarted = True
            return True
    return False


def call_video(event_key, nw_sock):
    nw_sock.transmit(event_key)

    
def mc_boot(_, nw_sock):
    nw_sock.transmit("idle")


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
        event_next_qeued: "self_check_q1",
    },

    "game_live": {
        pcf_out_add: [LightIO.pcfOut, BreakoutIO.pcfOut],
        pcf_out: [LightIO.gameReset, BreakoutIO.roomReset],
        event_script: set_live,
        event_next_qeued: "game_livePower"
    },

    "game_livePower": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.roomReset],
        event_delay: 0.5
    },

    "service_enable": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.service_enable],
    },

    "game_over": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.gameOver],
    },

    "hallway_preStage": {
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayStart],
    },
    "hallway_start": {
        pcf_in_add: ArbiterIO.pcfIn,
        pcf_in: ArbiterIO.entrance,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOn],
        event_condition: can_start_hallway
    },
    "hallway_on": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.lightOn,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOn]
    },

    "hallway_off": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.lightOff,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.hallwayOff],
    },

    # opening of the chinmey, fades in and out to set its fokus
    "chimney_opening": {
        pcf_in_add: LightIO.pcfIn,
        pcf_in: LightIO.chinmeySolved,
        pcf_out_add: [LightIO.pcfOut, FuseIo.pcfOut, PowerIO.pcfOut],
        pcf_out: [LightIO.chimneyOverride, FuseIo.mcOpened, PowerIO.emporeOff],
        event_next_qeued: "livingPower_offChimnneyOpend"
    },

    "water_solved": {
        pcf_in_add: WaterIO.pcfIn,
        pcf_in: WaterIO.uvActive,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.waterUV],
        event_next_qeued: "emporePower_off",
    },

    "fusebox_doorOpened": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.doorOpen
    },

    # boots up PCs from the floppy riddle, lights up the MC
    "fusebox_bootMC": {
        pcf_in_add: FuseIo.pcfIn,
        pcf_in: FuseIo.mcBoot,
        pcf_out_add: [BreakoutIO.pcfOut, LightIO.pcfOut, PowerIO.pcfOut],
        pcf_out: [BreakoutIO.mcBoot, LightIO.mcBoot, PowerIO.raum2On],
        event_next_qeued: "livingPower_offMCBoot",
        event_script: mc_boot
    },

    "breakout_solved": {
        pcf_in_add: BreakoutIO.pcfIn,
        pcf_in: BreakoutIO.solved,
        pcf_out_add: [BreakoutIO.pcfOut, LightIO.pcfOut, PowerIO.pcfOut],
        pcf_out: [BreakoutIO.setSolved, LightIO.gameSolved, PowerIO.livingOff],
    },

    "emporePower_on": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.emporeOn],
    },
    "emporePower_off": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.emporeOff],
    },
    "emporePower_offMCBoot": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.emporeOff],
        event_next_qeued: "livingPower_onMCBoot"
    },
    "livingPower_onChimnneyOpend":{
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOn],
        event_script: wait_for_chimney,
        event_next_qeued: "emporePower_on"
    },
    "livingPower_offChimnneyOpend":{
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOff],
        event_next_qeued: "livingPower_onChimnneyOpend"
    },
    
    "livingPower_on": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOn],
    },
    "livingPower_onAppartmentEnter": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOn],
        event_script: wait_for_lightEffekt,
        event_next_qeued: "emporePower_on"
    },
    "livingPower_onMCBoot": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOn],
        event_script: wait_for_lightEffekt2,
        event_next_qeued: "emporePower_on"
    },
    "livingPower_offMCBoot": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOff],
        event_next_qeued: "emporePower_offMCBoot"
    },
    
    "livingPower_off": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.livingOff],
    },
    "room2Power_on": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.raum2On],
    },
    "room2Power_off": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.raum2Off],
    },
    "servicePower_on": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.serviceOn],
    },
    "servicePower_off": {
        pcf_out_add: [PowerIO.pcfOut],
        pcf_out: [PowerIO.serviceOff],
    },
}


def setup_default_callbacks(list):
    for event_key in list.keys():
        event_data = list[event_key]

        if not (event_data.get(trigger_msg, False) and event_data.get(trigger_cmd, False)):
            triggers = re.split("_", event_key)
            if len(triggers) == 2:
                list[event_key][trigger_cmd] = triggers[0]
                list[event_key][trigger_msg] = triggers[1]


setup_default_callbacks(event_map)


# Only can be applied to non binary pinbased inputs
inverted_events = {

    "game_start": {
        pcf_in_add: ArbiterIO.pcfIn,
        pcf_in: ArbiterIO.entrance,
        pcf_out_add: [LightIO.pcfOut, FuseIo.pcfOut],
        pcf_out: [LightIO.hallwayStart, FuseIo.startGame],
        event_condition: start_game_condition,
    },

    "appartment_enter": {
        pcf_in_add: ArbiterIO.pcfIn,
        pcf_in: ArbiterIO.apartmentDoor,
        pcf_out_add: [LightIO.pcfOut],
        pcf_out: [LightIO.apartmentEnter],
        event_condition: can_enter_appartment,
        event_next_qeued: "livingPower_onAppartmentEnter"
    },
}


setup_default_callbacks(inverted_events)