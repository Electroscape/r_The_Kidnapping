#pragma once

#define relayAmount 2
#define open        0
#define closed      1
#define Hamburg     1

enum relays {
    labEntry,
    decon
};

enum relayInits {
    labEntry_init = closed,
    labExit_init = closed,
    decon_init = closed
};

int relayPinArray[relayAmount] = {
    labEntry,
    decon
};

int relayInitArray[relayAmount] = {
    labEntry_init,
    decon_init
};

enum brains {
    ledCeilBrain = 3
};


// --- Inputs IGNORE THE NAMING SCHEME, this is already transmitted as binary
enum IOPins {
    IO1,
    IO2,
    IO3,
    IO4
};


enum IO {
    lightOff = 1,
    lightNormal,
    lightRed,
    lightBlue,
    lightRachelAnnouncement,
    lightRachelEnd,
    lightDavidAnnouncement,
    labDoorLock,
    labDoorUnlock,
    deconTrigger,
};

#define outputCnt 0
#define inputCnt 4

static constexpr int clrLight[3] = {255,200,120};


int intputArray[inputCnt] = {
    IO1,
    IO2,
    IO3,
    IO4
};

int outputArray[outputCnt] = {};

