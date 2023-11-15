#pragma once

#define StageCount 2
#define PasswordAmount 1
#define MaxPassLen 4

// --- LED settings --- 
#define NR_OF_LEDS             1  /* Anzahl der Pixel auf einem Strang (Test 1 Pixel)                   */
#define STRIPE_CNT             3

#define doorOpen    0
#define doorClosed  1

#define relayAmount 1


enum stages {
    idle = 1, 
    solved = 2, 
};
int stageSum = ~( ~0 << StageCount );

int flagMapping[StageCount] {
    rfidFlag,   
    0          
};

char passwords[PasswordAmount][MaxPassLen] = {
    "AH"    // Rachel
};

int passwordMap[PasswordAmount] = {
    idle
};


enum brains {
    rfidLed
};



enum IOpins {
    IO_1,
    IO_2,
    IO_3,
    IO_4,
    IO_5, 
    IO_6,
    IO_7,                       
    IO_8,                                            
};

enum inputValues {  
    roomReset = 1, 
    setSolved           
};

enum outputValues {
    outSolved = 1,
};

#define outputCnt 1
#define inputCnt 2

int intputArray[inputCnt] = {
    IO_1,
    IO_2,
};

int outputArray[outputCnt] = {
    IO_3                      
};


enum relays {
    door
};

enum relayInits {
    doorInit = doorClosed
};

int relayPinArray[relayAmount] = {
    door,
};

int relayInitArray[relayAmount] = {
    doorInit,
};
