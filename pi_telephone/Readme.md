# Telephone_Kidnapping

Telephone module

python3 -m pip install -U pygame --user
sudo apt-get install libsdl2-mixer-2.0-0 


## **Libraries Used**

### Pygame

Pygame a cross platform set of python modules which is used for video games.
Its a library which retruns the interactions with a player when pressing on a keyboard.

**Resources**: I learned how to manage the library from this link <https://www.pygame.org/docs/> .

- A **CONFIG FILE** is created to store the directories and pins used with the raspberry pi 3B.

- Placing a **CURRENT WORKING DIRECTORY** command to print the running file directory, if you run the script from any point in the folder.

## **Functoinality**

The player starts to dial once he takes a call. Then a regular check on the number
entered is done until reaching the correct code to display the correct voice recording.

## **Notes**

- The sound recordings are stored in the **sounds folder**.
- The phone was used from the Rabuun room which was built by Cologne.

## Install client for language option

Language Option Installation

### **Install python on GameMaster PC**

- Use the **python-3.11.1-amd64.exe** to install python first.
- Add both files **Language_Option.py** and the logo file **logo.ico** on desktop.
- Then create a shortcut for the py script in desktop and change its logo using the following steps right click on py script > properties > Change Icon > browse the logo.ico file.

### **Important Notes**

- Change the **Ip address** in line 8 in the **Language_Option.py** script based on the one the telephone is using.
- Open the telephone first and then run the desktop icon and choose the language.
- **Initially** without pressing anything the language is german, no need to start the app.
