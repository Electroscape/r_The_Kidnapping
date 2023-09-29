#pragma once

#define relayAmount 4
#define open        0
#define closed      1

enum relays {
    pump_1,
    pump_2,
    table_light,
    table_magnet,
};

enum relayInits {
    pump_1_init = closed,
    pump_2_init = closed,
    table_light_init = closed,
    table_magnet_init = closed, // Wiring will be NC
};

int relayPinArray[relayAmount] = {
    pump_1,
    pump_2,
    table_light,
    table_magnet,
};

int relayInitArray[relayAmount] = {
    pump_1_init,
    pump_2_init,
    table_light_init,
    table_magnet_init,
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
};


enum IO {
    level_1 = 1 << 0,
    level_2 = 1 << 1,
    level_3 = 1 << 2,
    ledTable = 1 << 3,
};

#define outputCnt 0
#define inputCnt 4

static constexpr int clrLight[3] = {255,200,120};


int intputArray[inputCnt] = {
    IO1,
    IO2,
    IO3,
    IO4,
};

int outputArray[outputCnt] = {};

