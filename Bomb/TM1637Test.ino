#include <Arduino.h>
#include <TM1637Display.h>

// Module connection pins (Digital Pins)
#define CLK 2
#define DIO 3

#define CLK2 8
#define DIO2 9


int MINS_FIRST_DIGIT = 5;
int MINS_SECOND_DIGIT = 9;
int SEC_FIRST_DIGIT = 5;
int SEC_SECOND_DIGIT =  9;

const int buzzer = 4; //buzzer to arduino pin 4

int check = 5;
int ultimateCheck = 6;
bool flagChange= true;
bool twentyMinsPass = false;
int data[4];
String clock = "";
int clockNumber = 0;
int finalCode = 3491;
int buzzMidFreq = 11000
int buzzLowFreq = 13000
int buzzHighFreq = 9000

// The amount of time (in milliseconds) between tests
#define TIME_DELAY   1000

TM1637Display display1(CLK, DIO);
TM1637Display display2(CLK2, DIO2);

uint8_t cleardata[] = { 0x00, 0x00, 0x00, 0x00 };
const uint8_t allON[] = {0xff, 0xff, 0xff, 0xff};

void buzz(int freq){
  tone(buzzer, freq); 
  delay(100);       
  noTone(buzzer);     
  delay(900);       
}



void setup()
{
  Serial.begin(9600);
  pinMode(check, INPUT);
  pinMode(ultimateCheck, INPUT_PULLUP);
  pinMode(buzzer, OUTPUT); // Set buzzer - pin 4 as an output
  

  display1.clear();
  display2.clear();
  display1.setBrightness(0x0f);
  display2.setBrightness(0x0f);

}

void loop()
{

  if (digitalRead(check) == HIGH && digitalRead(ultimateCheck) == LOW ) {
    display1.setSegments(cleardata);

    delay(TIME_DELAY);
    noTone(buzzer);     // Stop sound...
    //display final code
    display2.showNumberDec(finalCode);
    Serial.println("Game is Solved!!");

  }
  else {

    display2.clear();
    data[0] = MINS_FIRST_DIGIT;
    data[1] = MINS_SECOND_DIGIT;
    data[2] = SEC_FIRST_DIGIT;
    data[3] = SEC_SECOND_DIGIT;

    for ( int i = 0 ; i < 4 ; i++) {
      clock = clock + data[i];
    }
    clockNumber = clock.toInt();


    //display.setSegments(data,0b11100000);
    display1.showNumberDecEx(clockNumber, 0b01000000, false, 4);
    SEC_SECOND_DIGIT--;
    //delay(TIME_DELAY);
    Serial.print(SEC_SECOND_DIGIT);
    //buzz();
    if (MINS_FIRST_DIGIT == 4 && MINS_SECOND_DIGIT == 5){
      flagChange = false;
    }
    if (MINS_FIRST_DIGIT == 2 && MINS_SECOND_DIGIT == 5){
      twentyMinsPass = true;
    }

    if (flagChange){
      buzz(buzzHighFreq);
    }
    else{
      if (twentyMinsPass){
        buzz(buzzLowFreq);
      }
      else{
      buzz(buzzMidFreq);
      }
    }

    if (MINS_SECOND_DIGIT == 0 && SEC_FIRST_DIGIT == 0 && SEC_SECOND_DIGIT < 0) {
      MINS_FIRST_DIGIT--;
      SEC_SECOND_DIGIT = 9;
      SEC_FIRST_DIGIT = 5;
      MINS_SECOND_DIGIT = 9;
    }

    else if (SEC_FIRST_DIGIT == 0 && SEC_SECOND_DIGIT < 0) {
      MINS_SECOND_DIGIT--;
      SEC_FIRST_DIGIT = 5;
      SEC_SECOND_DIGIT = 9;
    }

    else if (SEC_SECOND_DIGIT < 0) {
      SEC_SECOND_DIGIT = 9;
      SEC_FIRST_DIGIT--;
    }
    else{
      Serial.println("");
    }

  }

  clock = "";




}
