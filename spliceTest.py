#Setting up a file to test the pi inputs from the splicer
#Run this script to open a loop that monitors and reports on the Lick_ and Shutter_inport pins on a raspberry pi. Allows for debugging those inputs with real-time feedback.

import RPi.GPIO as GPIO
import time
import numpy as np
import easygui
#import sys

#%% Setup
# Setup pi board
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

#define the pin that goes to the beam break for shutter open/close detection
Shutter_inport = 20 # Should be wired to Shutter Mag Sensor channel
GPIO.setup(Shutter_inport, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#define the pin that goes to the lick detector (the photodiode)
Lick_inport = 21 # Should be wired to Lick TTL channel
GPIO.setup(Lick_inport, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


ShutterWas = GPIO.input(Shutter_inport)
LickWas = GPIO.input(Lick_inport)
print(f'Shutter Channel initial state: {ShutterWas}')
print(f'Lick Channel initial state: {LickWas}')

try:
    print("Opening testing loop, ctrl+C to close")
    while True:
        ShutterIs = GPIO.input(Shutter_inport)
        LickIs = GPIO.input(Lick_inport)
        
        if (ShutterWas != ShutterIs):
            print(f'Shutter is: {ShutterIs}')
            ShutterWas = ShutterIs
        if (LickWas != LickIs):
            print(f'Lick Channel is: {LickIs}')
            LickWas = LickIs
except:
    print("Ending Script")
