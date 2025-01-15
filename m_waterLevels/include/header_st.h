#pragma once

#define relayAmount 4
#define open        0
#define closed      1

enum relays {
    pump_1,
    pump_2,
    table_light,
    magnets,    // Zwinger and drawer
};

enum relayInits {
    pump_1_init = closed,
    pump_2_init = closed,
    table_light_init = closed,
    magnets_init = closed, // Wiring will be NC for both
};

int relayPinArray[relayAmount] = {
    pump_1,
    pump_2,
    table_light,
    magnets,
};

int relayInitArray[relayAmount] = {
    pump_1_init,
    pump_2_init,
    table_light_init,
    magnets_init,
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
    IO5,
};


enum inputs {
    level_1 = 1 << 0,
    level_2 = 1 << 1,
    level_3 = 1 << 2,
    ledTable = 1 << 3,
};


enum outputs {
    solved = 1 << 4
};


#define outputCnt 1
#define inputCnt 4

static constexpr int clrLight[3] = {255,200,120};

int intputArray[inputCnt] = {
    IO1,
    IO2,
    IO3,
    IO4,
};

int outputArray[outputCnt] = {
    IO5
};

