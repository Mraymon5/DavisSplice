#Setting up a file to test the pi inputs from the splicer
import RPi.GPIO as GPIO
import time
import numpy as np
import easygui
#import sys

#%% Setup
# Setup pi board
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

#define the pin that goes to the beam break for shutter open/close detection
Shutter_inport = 5 # Should be wired to Shutter Mag Sensor channel
GPIO.setup(Shutter_inport, GPIO.IN)

#define the pin that goes to the lick detector (the photodiode)
Lick_inport = 7 # Should be wired to Lick TTL channel


ShutterWas = GPIO.input(Shutter_inport)
LickWas = GPIO.input(Lick_inport)
print(f'Shutter Channel is: {ShutterWas}')
print(f'Lick Channel is: {LickWas}')

try:
    print("Opening testing loop, ctrl+C to close")
    while True:
        ShutterIs = GPIO.input(Shutter_inport)
        LickIs = GPIO.input(Lick_inport)
        
        if (ShutterWas != ShutterIs):
            print(ShutterIs)
            ShutterWas = ShutterIs
        if (LickWas != LickIs):
            print(LickIs)
            LickWas = LickIs
except:
    print("Ending Script")