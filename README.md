# r_The_Kidnapping

Repository of the room The Kidnapping

## Content
this repository contains the arduino code for the following riddles
 - Breakout:
   - A riddle using RFID to open a door and with some LED effects
   
## Usage
This project is build  with PlattformIO and the riddles are in individual folders to be opened as a plattformio project.
Each Riddle contains a `src` folder for the actual code and `Include` folders to take settings from header files.
The libraries used are found in https://github.com/Electroscape/lib_arduino and the library path for the build is set inside plattformio.ini within each riddle folder.

Building is done with plattformIO from the .ino file with the same name as the riddle inside `src`. 