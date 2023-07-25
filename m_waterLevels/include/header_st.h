#pragma once

#define relayAmount 2
#define open        0
#define closed      1

enum relays {
    pump_1,
    pump_2
};

enum relayInits {
    pump_1_init = closed,
    pump_2_init = closed
};

int relayPinArray[relayAmount] = {
    pump_1,
    pump_2
};

int relayInitArray[relayAmount] = {
    pump_1_init,
    pump_2_init
};

enum brains {
    ledBrain = 2
};


// --- Inputs IGNORE THE NAMING SCHEME, this is already transmitted as binary
enum IOPins {
    IO1,
    IO2,
    IO3,
    IO4,
    IO5
};


enum IO {
    level_1 = 1 << 0,
    level_2 = 1 << 1,
    level_3 = 1 << 2,
    level_4 = 1 << 3,
    level_5 = 1 << 4,
};

#define outputCnt 0
#define inputCnt 5

static constexpr int clrLight[3] = {255,200,120};


int intputArray[inputCnt] = {
    IO1,
    IO2,
    IO3,
    IO4,
    IO5
};

int outputArray[outputCnt] = {};

