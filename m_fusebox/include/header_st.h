#pragma once

#define relayAmount 5
#define open        0
#define closed      1

enum brains {
    ledBrain = 2
};

enum relais {
    door,
    alarm,
    mcBoot,
    toggleOff,
    toggleOn,
};

enum relayInits {
    door_init = open,
    alarm_init = open,
    mcBoot_init = closed,
    toggleOff_init = closed,
    toggleOn_init = closed,
};

int relayPinArray[relayAmount] = {
    door,
    alarm,
    mcBoot,
    toggleOff,
    toggleOn,
};

int relayInitArray[relayAmount] = {
    door_init,
    alarm_init,
    mcBoot_init,
    toggleOff_init,
    toggleOn_init,
};


// --- Inputs IGNORE THE NAMING SCHEME, this is already transmitted as binary
enum IOPins {
    IO1,
    IO2,
    IO3,
    IO4,
    IO5,
    IO6,
    IO7,
    IO8,
};


enum stages {
    prestage = 1,
    hallway = 2,
    missionControlUnlock = 4,
    missionControlBoot = 8,
    completed = 16,
};


// 2 IOs left so 3 states can be overridden here?
enum inputs {
    fuse_1 = 1 << 0,
    fuse_2 = 1 << 1,
    fuse_3 = 1 << 2,
    fuse_4 = 1 << 3,
    fuse_5 = 1 << 4,
    lid_reed = 1 << 5,
    start_game = 1 << 6,
    mc_opened = 1 << 7
};


enum outputs {
    solved_1 = 1,
    solved_2 = 2
};


#define outputCnt 0
#define inputCnt 8

static constexpr int clrLight[3] = {255,200,120};

int intputArray[inputCnt] = {
    IO1,
    IO2,
    IO3,
    IO4,
    IO5,
    IO6,
    IO7,
    IO8,
};

int outputArray[outputCnt] = {
};

