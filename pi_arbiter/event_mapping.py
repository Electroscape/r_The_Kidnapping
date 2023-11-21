import requests
import subprocess
from enum import IntEnum

# http://www.compciv.org/guides/python/fundamentals/dictionaries-overview/
# defaults?

# these are the pcf addresses, first 3 are Arbiter -> Brain as outputs
# last 3 are Brain -> Arbiter inputs

# for rev 0.1
# [0x38, 0x39, 0x3A, 0x3C, 0x3D, 0x3E]
# for rev 0.2 and onwards
# [0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]

#
laserlock_out_pcf = 0
# also used for the cleanroom rigger
airlock_out_pcf = 1
lab_light_out_pcf = 2
# inputs
laserlock_in_pcf = 4
# If we need more inputs this is the prime candidate to consolidate with the above
laserlock_in_2_pcf = 3
airlock_in_pcf = 5
analyzer_in_pcf = laserlock_in_2_pcf
locker_in_pcf = laserlock_in_2_pcf      # used for the service enable/disable
locker_out_pcf = airlock_out_pcf
dispenser_out_pcf = lab_light_out_pcf


sound = "sound"
is_fx = "is_fx"
sound_id = "id"

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


class LaserlockOut(IntEnum):
    usb_boot = 1
    david_end = 2
    rachel_end = 3
    light_off = 4
    cleanupLight = 5
    failedBootTrigger = 6
    bootupTrigger = 7
    rachel_end_announce = 8
    skip_to_seperation = 9      # in case the mother crashes lik in in HH


class LaserlockIn(IntEnum):
    david = 1
    rachel = 2
    seperationEnd = 3
    davidSeperated = 4     # status for T1
    rachelSeperated = 5    # status for T1
    timeout = 6


class LockerIn(IntEnum):
    serviceEnable = 1 << 4
    serviceDisable = 1 << 5


class LockerOut(IntEnum):
    serviceEnable = 1 << 3
    serviceDisable = 1 << 4
    selfDestruct = 24


labLight_trigger = "labLight"
ending_trigger = "upload"
lab_light_off = 1
lab_light_white = 2
lab_light_standby = 3
lab_light_on = 4
lab_rachel_end_announce = 5
lab_rachel_end = 6
lab_david_end_announce = 7

lab_dishout = 1 << 4
lab_dish1 = 32
lab_dish2 = 32 + 16
lab_dish3 = 64
lab_dish4 = 64 + 16
lab_dish5 = 64 + 32
lab_dish_rachel_end_announce = 64 + 32 + 16
lab_dish_david_end = 128
lab_dish_rachel_end = 128 + 16

# Begin, Video, Fumigation, SterilizationIntro, Sterilization, BioScanIntro, BioScan, BioScanDenied, Wrong, Opening

binary_pcfs = [airlock_in_pcf, laserlock_in_pcf]

blank_screen_pid = subprocess.Popen(["cvlc", "media/black_screen.jpg", "--no-embedded-video", "--fullscreen",
                                     "--no-video-title", "--video-wallpaper", "--quiet", "--loop"])


class States:
    def __init__(self):
        self.laserlock_door_armed = False
        self.laserlock_door_opened = False
        self.laserlock_fixed = False
        self.usb_booted = False
        self.truth_played = False
        self.upload_elancell = False
        self.upload_Rachel = False
        self.service = False
        self.stream_active = False


states = States()


def play_elancell_intro(*args):
    blank_screen_pid.kill()
    print("playing elancell intro")
    subprocess.Popen(['cvlc', "media/Welcome to Elancell_w_Audio.mp4",
                      "--no-embedded-video", "--fullscreen", '--no-video-title', '--video-on-top', '--quiet'])


def call_video(event_key, nw_sock):
    nw_sock.transmit(event_key)


class LaserLock:
    @staticmethod
    def arm_door(*args):
        states.laserlock_door_armed = True
        states.laserlock_door_opened = False

    @staticmethod
    def door_open_condition():
        if states.laserlock_door_armed and not states.laserlock_door_opened:
            states.laserlock_door_opened = True
            return True
        return False

    @staticmethod
    # @todo: just include set_fixed into condition
    def fixed_condition(*args):
        if not states.laserlock_fixed:
            states.laserlock_fixed = True
            return True
        return False

    @staticmethod
    def broken_conditions(*args):
        if states.laserlock_fixed:
            states.laserlock_fixed = False
            return True
        return False

    @staticmethod
    def play_truth_condition(*args):
        if not states.truth_played:
            states.truth_played = True
            states.stream_active = True
            return True
        return False

    @staticmethod
    def start_stream(*args):
        if not states.stream_active:
            states.stream_active = True
            return True
        return False


class USBScripts:
    @staticmethod
    def rachel_enabled_condition(*args):
        if not states.upload_Rachel and not states.upload_elancell:
            states.upload_Rachel = True
            return True
        return False

    @staticmethod
    def rachel_disabled_condition():
        if states.upload_Rachel:
            states.upload_Rachel = False
            return True
        return False

    @staticmethod
    def elancell_enabled_condition(*args):
        if not states.upload_elancell and not states.upload_Rachel:
            states.upload_elancell = True
            return True
        return False

    @staticmethod
    def elancell_disabled_condition(*args):
        if states.upload_elancell:
            states.upload_elancell = False
            return True
        return False

    @staticmethod
    def boot_condition(*args):
        usb_status = states.usb_booted
        if not usb_status:
            states.usb_booted = True
            return True
        else:
            return False


event_map = {
    # @todo: maybe add a callback here to the FE?
    # @todo: shall we automatically end the any service mode here?
    "self_check": {
        trigger_cmd: "self",
        trigger_msg: "check",
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [LaserlockOut.failedBootTrigger],
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "boot"
        },
        sound: {
            sound_id: 3
        },
        event_script: call_video,
        event_next_qeued: "self_check_q1"
    },
    "self_check_q1": {
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "david"
        },
        event_next_qeued: "self_check_q2"
    },
    "self_check_q2": {
        event_delay: 15,
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "disconnect"
        },
        event_next_qeued: "self_check_q3"
    },
    "self_check_q3": {
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "empty"
        },
    },
    "airlock_begin": {
        trigger_cmd: "airlock",
        trigger_msg: "begin",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 1,
        sound: {
            is_fx: True,
            sound_id: 0
        }
    },
    "airlock_begin_atmo": {
        trigger_cmd: "airlock",
        trigger_msg: "begin",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 1,
        sound: {
            is_fx: False,
            sound_id: 0
        }
    },
    # Sound stops to early?
    "airlock_intro": {
        trigger_cmd: "airlock",
        trigger_msg: "intro",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 2,
        event_script: play_elancell_intro,
        event_delay: 10,
        # this is the sound to go along with teh video
        sound: {
            is_fx: True,
            sound_id: 24
        }
    },
    "airlock_fumigation": {
        trigger_cmd: "airlock",
        trigger_msg: "fumigation",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 7,
        sound: {
            sound_id: 26
        }
    },
    "airlock_sterilizationIntro": {
        trigger_cmd: "airlock",
        trigger_msg: "sterilizationIntro",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 5,
        sound: {
            sound_id: 23
        }
    },
    "airlock_UV": {
        trigger_cmd: "airlock",
        trigger_msg: "UV",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 4,
        sound: {
            sound_id: 2
        }
    },
    "airlock_BioScanIntro": {
        trigger_cmd: "airlock",
        trigger_msg: "BioScanIntro",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 8,
        sound: {
            sound_id: 22
        }
    },
    "airlock_BioScan": {
        trigger_cmd: "airlock",
        trigger_msg: "BioScan",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 9,
        sound: {
            sound_id: 25
        }
    },
    "airlock_BioScanDenied": {
        trigger_cmd: "airlock",
        trigger_msg: "BioScanDenied",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 10,
        sound: {
            sound_id: 21
        }
    },
    "airlock_wrong": {
        trigger_cmd: "airlock",
        trigger_msg: "wrong",
        pcf_in_add: airlock_in_pcf,
        pcf_in: 3,
        sound: {
            is_fx: True,
            sound_id: 1
        }
    },
    "airlock_opening": {
        pcf_in_add: airlock_in_pcf,
        pcf_in: 6,
        sound: {
            is_fx: False,
            sound_id: 1
        }
    },
    "usb_boot": {
        trigger_cmd: "usb",
        trigger_msg: "boot",
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "boot"
        },
        event_condition: USBScripts.boot_condition,
        event_delay: 72,
        event_script: call_video,
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [LaserlockOut.usb_boot],
        sound: {
            is_fx: False,
            sound_id: 2
        },
    },
    "laserlock_skip": {
        trigger_cmd: "laserlock",
        trigger_msg: "skip",
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [LaserlockOut.skip_to_seperation],
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "empty"
        },
        event_next_qeued: "laserlock_lockout_tr1"
    },
    "laserlock_fail": {
        trigger_cmd: "laserlock",
        trigger_msg: "fail",
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [LaserlockOut.failedBootTrigger],
        sound: {
            sound_id: 3
        }
    },
    "laserlock_cable_fixed": {
        pcf_in_add: laserlock_in_2_pcf,
        pcf_in: 1 << 0,
        event_condition: LaserLock.fixed_condition,
        fe_cb: {
            fe_cb_cmd: "laserlock",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "fixed"
        }
    },
    "laserlock_bootdecon": {
        trigger_cmd: "laserlock",
        trigger_msg: "access",
        pcf_out_add: [laserlock_out_pcf],
        pcf_out: [LaserlockOut.bootupTrigger],
        event_script: LaserLock.arm_door,
        # event_delay: 0,
        sound: {
            sound_id: 4,
        }
    },
    "laserlock_welcome_david": {
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.david,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_standby],
        sound: {
            sound_id: 15
        },
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "david"
        }
    },
    "laserlock_welcome_rachel": {
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.rachel,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_standby],
        sound: {
            sound_id: 16
        },
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "rachel"
        }
    },
    "laserlock_auth_tr1_david": {
        trigger_cmd: "ter1",
        trigger_msg: "david",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.davidSeperated,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_on],
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "david"
        },
        sound: {
            sound_id: 4,
            is_fx: False
        }
    },
    "laserlock_auth_tr2_rachel": {
        trigger_cmd: "ter2",
        trigger_msg: "rachel",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.davidSeperated,
        event_next_qeued: "play_truth",
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "rachel"
        }
    },
    "play_truth": {
        trigger_cmd: "play",
        trigger_msg: "truth",
        event_condition: LaserLock.play_truth_condition,
        event_script: call_video,
        fe_cb: {
            fe_cb_cmd: "usbBoot",
            fe_cb_tgt: "tr3",
            fe_cb_msg: "boot"
        }
    },
    "laserlock_auth_tr1_rachel": {
        trigger_cmd: "ter1",
        trigger_msg: "rachel",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.rachelSeperated,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_on],
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "rachel"
        },
        sound: {
            sound_id: 4,
            is_fx: False
        }
    },
    "laserlock_auth_tr2_david": {
        trigger_cmd: "ter2",
        trigger_msg: "david",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.rachelSeperated,
        event_next_qeued: "display_securityAutomatic",
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "david"
        }
    },
    "laserlock_lockout_tr1": {
        trigger_cmd: "ter1",
        trigger_msg: "empty",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.seperationEnd,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_standby],
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "empty"
        },
        sound: {
            is_fx: False,
            sound_id: 2
        },
    },
    "laserlock_lockout_tr2": {
        trigger_cmd: "ter2",
        trigger_msg: "empty",
        pcf_in_add: laserlock_in_pcf,
        pcf_in: LaserlockIn.seperationEnd,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_standby],
        fe_cb: {
            fe_cb_cmd: "auth",
            fe_cb_tgt: "tr2",
            fe_cb_msg: "empty"
        }
    },
    "display_security": {
        trigger_cmd: "display",
        trigger_msg: "security",
        event_script: call_video,
    },
    "display_securityAutomatic": {
        event_condition: LaserLock.start_stream,
        event_script: call_video,
    },
    "play_biovita": {
        trigger_cmd: "play",
        trigger_msg: "biovita",
        event_script: call_video,
    },
    "dispenser_dishout": {
        trigger_cmd: "dispenser",
        trigger_msg: "dishout",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dishout]
    },
    "dispenser_dish1": {
        trigger_cmd: "dispenser",
        trigger_msg: "dish1",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish1]
    },
    "dispenser_dish2": {
        trigger_cmd: "dispenser",
        trigger_msg: "dish2",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish2]
    },
    "dispenser_dish3": {
        trigger_cmd: "dispenser",
        trigger_msg: "dish3",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish3]
    },
    "dispenser_dish4": {
        trigger_cmd: "dispenser",
        trigger_msg: "dish4",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish4]
    },
    "dispenser_dish5": {
        trigger_cmd: "dispenser",
        trigger_msg: "dish5",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish5]
    },
    "analyzer_run1": {
        trigger_cmd: "analyzer",
        # sythesis number correct
        trigger_msg: "run1Right",
        event_script: call_video,
        pcf_in_add: analyzer_in_pcf,
        pcf_in: 1 << 2,
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_dish5]
    },
    "analyzer_run2": {
        trigger_cmd: "analyzer",
        # sythesis number correct
        trigger_msg: "run2Right",
        pcf_in_add: analyzer_in_pcf,
        pcf_in: 1 << 3,
        fe_cb: {
            fe_cb_cmd: "elancell",
            fe_cb_msg: "synthesized",
            fe_cb_tgt: "tr2"
        }
    },
    "reset_atmo": {
        sound: {
            is_fx: False,
            sound_id: -1
        },
        pcf_out_add: [lab_light_out_pcf, laserlock_out_pcf],
        pcf_out: [lab_light_off, LaserlockOut.light_off]
    },
    "cleanroom": {
        trigger_cmd: "cleanroom",
        trigger_msg: "unlock",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [10],
        sound: {
            is_fx: False,
            sound_id: 5
        }
    },
    "lab_light_off": {
        trigger_cmd: labLight_trigger,
        trigger_msg: "off",
        pcf_out_add: [lab_light_out_pcf],
        pcf_out: [lab_light_off]
    },
    "time_announcement": {
        trigger_cmd: "time",
        trigger_msg: "announcement",
        event_script: call_video,
    },
    "end_timeup": {
        trigger_cmd: "end",
        trigger_msg: "timeup",
        event_script: call_video,
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, airlock_out_pcf, lab_light_out_pcf],
        pcf_out: [LaserlockOut.rachel_end, lab_rachel_end, AirlockOut.rachel_end, lab_rachel_end],
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "disconnect"
        },
        sound: {
            is_fx: False,
            sound_id: 6
        },
    },
    "end_rachel_announce": {
        trigger_cmd: ending_trigger,
        trigger_msg: "rachel",
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, airlock_out_pcf, lab_light_out_pcf],
        pcf_out: [LaserlockOut.rachel_end_announce, lab_rachel_end_announce, AirlockOut.rachel_announce, lab_dish_rachel_end_announce],
        event_script: call_video,
        event_next_qeued: "end_rachel"
    },
    "end_rachel": {
        trigger_cmd: ending_trigger,
        trigger_msg: "rachelEnd",
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, airlock_out_pcf, lab_light_out_pcf, locker_out_pcf],
        pcf_out: [LaserlockOut.rachel_end, lab_rachel_end, AirlockOut.rachel_end, lab_dish_rachel_end, LockerOut.selfDestruct],
        event_delay: 92,
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "disconnect"
        },
        sound: {
            is_fx: False,
            sound_id: 6
        },
    },
    "end_david_announce": {
        trigger_cmd: ending_trigger,
        trigger_msg: "elancell",
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, airlock_out_pcf, lab_light_out_pcf],
        pcf_out: [LaserlockOut.david_end, lab_david_end_announce, AirlockOut.david_end, lab_david_end_announce],
        event_script: call_video
    },
    "end_self_destuction": {
        trigger_cmd: ending_trigger,
        trigger_msg: "SelfDestruction",
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, airlock_out_pcf, lab_light_out_pcf],
        pcf_out: [LaserlockOut.rachel_end, lab_rachel_end, AirlockOut.rachel_end, lab_rachel_end],
        fe_cb: {
            fe_cb_tgt: "tr1",
            fe_cb_cmd: "usbBoot",
            fe_cb_msg: "disconnect"
        },
        sound: {
            is_fx: False,
            sound_id: 6
        },
    },
    "service_mode_enable": {
        trigger_cmd: "service",
        trigger_msg: "on",
        pcf_in: LockerIn.serviceEnable,
        pcf_in_add: locker_in_pcf,
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, locker_out_pcf],
        pcf_out: [LaserlockOut.cleanupLight, lab_light_white, LockerOut.serviceEnable],
        # event_condition: GeneralConditions.service_enable
    },
    "service_mode_disable": {
        trigger_cmd: "service",
        trigger_msg: "off",
        pcf_in: LockerIn.serviceDisable,
        pcf_in_add: locker_in_pcf,
        pcf_out_add: [laserlock_out_pcf, lab_light_out_pcf, locker_out_pcf],
        pcf_out: [LaserlockOut.light_off, lab_light_off, LockerOut.serviceDisable],
        # event_condition: GeneralConditions.service_disable
    }
}

# Only can be applied to non binary pinbased inputs
inverted_events = {
    "laserlock_cable_broken": {
        pcf_in_add: laserlock_in_2_pcf,
        pcf_in: 1 << 0,
        event_condition: LaserLock.broken_conditions,
        fe_cb: {
            fe_cb_cmd: "laserlock",
            fe_cb_tgt: "tr1",
            fe_cb_msg: "broken"
        }
    },
    "laserlock_door_opened": {
        pcf_in_add: laserlock_in_2_pcf,
        pcf_in: 1 << 1,
        event_condition: LaserLock.door_open_condition,
        sound: {
            sound_id: 3,
            # yes its actually an atmo
            is_fx: False
        }
    },
}






