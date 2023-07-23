/**
 * @file m_laserlock.cpp
 * @author Martin Pek (martin.pek@web.de)
 * @brief controls a 
 * inputs via RFID and Keypad
 * @version 0.1
 * @date 2022-09-09
 * 
 * @copyright Copyright (c) 2022
 * 
 *  TODO: 
 * - double post of clean airlock & decontamination
 * - enumerating brain types
 * 🔲 add feedback to close the door when tryint to lock
 *  6. Wrong code entered on access module -> "Access denied" currently not implemented
 * ✅ add numbering of brains to header to make changes easiers
 * in between stage or text for unlocking with rfid
 *  Q:
 * 🔲 Timeout needs to send wrongres
 * 🔲 booting text on startup
 * 🔲 consider using laststage for the switch cases?
 * 
 */


#include <stb_mother.h>
#include <stb_mother_IO.h>
#include <stb_keypadCmds.h>
#include <stb_oledCmds.h>
#include <stb_mother_ledCmds.h>


#include "header_st.h"

// using the reset PCF for this
PCF8574 inputPCF;
STB_MOTHER Mother;
STB_MOTHER_IO MotherIO;

int lastState = -1;


void enableWdt() {
    wdt_enable(WDTO_8S);
}



void handleInputs() {

    int result = MotherIO.getInputs();

    if (lastState == result) {
        return;
    }
    lastState = result;

    unsigned long startTime = millis();
    Serial.println(result);

    switch (result) {
        case lightOff: 
            Mother.motherRelay.digitalWrite(labEntry, closed);
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
        break;
        case lightNormal: 
            Mother.motherRelay.digitalWrite(labEntry, open);
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, clrLight, 60);
        break;
        case lightRed:
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 40);
            
        break;
        case lightBlue:
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlue, 55);
        break;
        case lightRachelAnnouncement:
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 30);
            Mother.motherRelay.digitalWrite(labEntry, open);
            // @todo unlock door
        break;
        case lightRachelEnd:
            Mother.motherRelay.digitalWrite(labEntry, open);
            wdt_disable();
            #ifdef Hamburg
                LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 60);
                /* delay(41000); // Video Rachel
                delay(34000); // Video Proceed to airlock start at second "remain calm" */
                LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 50);
                delay(200);
                
                LED_CMDS::blinking(Mother, ledCeilBrain,LED_CMDS::clrBlack,LED_CMDS::clrYellow,950,50,100,100,PWM::set1);
                
                delay(10000); // Delay Countdown

                LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 50);
                delay(1000);
                for (int i=0; i<4; i++) {
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 100);
                    delay(200);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrYellow, 100);
                    delay(100);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlue, 100);
                    delay(100);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                }
                delay(500);
                LED_CMDS::blinking(Mother, ledCeilBrain,LED_CMDS::clrBlack,LED_CMDS::clrRed,10,10,100,10,PWM::set1);
                delay(1000);
                for (int i=0; i<3; i++) {
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 60);
                    delay(400);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrYellow, 60);
                    delay(200);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlue, 100);
                    delay(200);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                }
                delay(500);
                LED_CMDS::blinking(Mother, ledCeilBrain,LED_CMDS::clrBlack,LED_CMDS::clrRed,10,10,100,10,PWM::set1);
                delay(1000);
                for (int i=0; i<3; i++) {
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 30);
                    delay(650);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrYellow, 30);
                    delay(325);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlue, 100);
                    delay(325);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                }
                delay(500);
                LED_CMDS::blinking(Mother, ledCeilBrain,LED_CMDS::clrBlack,LED_CMDS::clrRed,10,10,100,10,PWM::set1);
                delay(1000);
                for (int i=0; i<3; i++) {
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrRed, 30);
                    delay(900);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrYellow, 30);
                    delay(450);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlue, 100);
                    delay(450);
                    LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);
                    delay(300);
                }
                LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 1000);           
           #else
                while ((millis() - startTime) < (unsigned long) 2000) {
                    LED_CMDS::fade2color(Mother, ledCeilBrain, LED_CMDS::clrRed, 30, LED_CMDS::clrBlack, 30, 600, 1);
                    delay(600);
                    LED_CMDS::fade2color(Mother, ledCeilBrain, LED_CMDS::clrBlack, 30, LED_CMDS::clrRed, 30, 600, 1);
                    delay(600);
                }
                LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrBlack, 100);            
            #endif              
            wdt_enable(WDTO_8S);
        break;
        case lightDavidAnnouncement:
            Mother.motherRelay.digitalWrite(labEntry, open);
            LED_CMDS::setAllStripsToClr(Mother, ledCeilBrain, LED_CMDS::clrGreen, 40);
        break;
        case IO::deconTrigger:
            Mother.motherRelay.digitalWrite(decon, open);
            delay(5000);
            Mother.motherRelay.digitalWrite(decon, closed);
        break;
        default: break;
    }

}


void setup() {

    Mother.begin();
    // starts serial and default oled
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    enableWdt();

    // technicall 3 but for the first segments till unlocked there is no need
    Mother.rs485SetSlaveCount(0);
  
    wdt_reset();
}


void loop() {
    handleInputs();    
    wdt_reset();
}




