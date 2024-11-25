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


print(f'Shutter Channel is: {GPIO.input(Shutter_inport)}')
print(f'Lick Channel is: {GPIO.input(Lick_inport)}')

    while shutteropen == 0:
        if GPIO.input(Shutter_inport) == GPIO.LOW:     #if IR beam is broken
            shutteropen = 1                     #break out of while loop