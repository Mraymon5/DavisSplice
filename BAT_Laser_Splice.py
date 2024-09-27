#This should activate laser for all trials in a session
#When there is a lick (light flash) detected by a photodiode (GPIO is greater than GOPI.low)
#Only during laser trials, when shutter is up, when lick is detected

#Created by Kathleen Maigler
#Modified by Martin Raymond

#import things
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
Shutter_inport = 5
GPIO.setup(Shutter_inport, GPIO.IN)

#define the pin that goes to the lick detector (the photodiode)
Lick_inport = 7

#%% Laser Trigger Function, for laser on every trial            
def laser_trigger_all(laser_ports = [22], trial_duration = 5, NTrials = None, subj_id = None, maxWait = 60, ITI = 10):
    r'''
    Run a Davis Rig session with laser trials triggered by licking. This version triggers the laser on every trial.

    :param int laser_ports: A single value giving the IO pin on the Pi that outputs to the laser driver
    :param int trial_duration: A single value giving the duration of the licking period/ duration of laser on time
    :param int NTrials: A single value giving the number of trials
    :param str subj_id: A string giving the ID of the animal
    :param int maxWait: A single value giving the max wait time between shutter opening and 1st lick
    :param int ITI: A single value giving the time between the shutter closing at the end of one trial and opening for the next trial
    :return: A csv named with the animal ID and the date, giving some metadata about the session
    '''
    #Define the laser ports and set them as outputs
    for i in laser_ports:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)

    #Get user inputs if they have not been provided
    if not NTrials:
        taste_seq = easygui.multenterbox(msg = 'Enter the number of taste presentations:', 
                                         fields = ['Number of Trials'])
        taste_seq = taste_seq[0].split(',')
        NTrials = int(taste_seq[0])
    if not subj_id:
        subj_id = easygui.multenterbox(msg = 'Enter the animal ID:', fields = ['Animal ID'])
 
    #create laser order for each taste
    laser_trials = np.ones(NTrials)

    print("Number of trials: " + str(NTrials))
    print("Laser Sequence: " + str(laser_trials))

    #Save laser trial order into a text file
    with open("{}_trials_order_{}.txt".format(subj_id[0],time.strftime("%Y%m%d")), 'w') as laserfile:
        OutText = "Animal_ID,NTrials,StartTime" + "\n" + str(subj_id[0]) + "," + str(NTrials) + "," + str(time.strftime("%H:%M:%S"))
        laserfile.write(OutText)

    print('Waiting for beam break signal....\nPress Ctrl-C to quit!')


    #Initialize the lick sensor channel
    GPIO.setup(Lick_inport, GPIO.OUT)
    GPIO.output(Lick_inport, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(Lick_inport, GPIO.IN) #Change the pin back to input
#    while not GPIO.input(Lick_inport):
#        time.sleep(1)
#        print('no light')
#    print(GPIO.input(Lick_inport))
#    print(GPIO.input(Lick_inport))

    for trial in range(NTrials):
                             
        shutteropen = 0
        print("Shutter closed, ready to open")
        while shutteropen == 0:
            if GPIO.input(Shutter_inport) == GPIO.LOW:     #if IR beam is broken
                shutteropen = 1                     #break out of while loop
                time_trial_start = time.time() #start the trial timer
                
                #Report the trial type
                if int(laser_trials[trial]) == 1:
                    print('Shutter open, Trial ' + str(trial) + '. This is a laser trial')
                else:
                    print('Shutter open, Trial ' + str(trial) + '. This is a control trial')
                    
                #Start looking for licks
                if (rc_time(Lick_inport, maxWait, time_trial_start) > 0):
                    #if lick detected/light detected and it is under 60 seconds max wait time since shutter was raised/start of trial
                    if int(laser_trials[trial]) == 1:
                        for laser in laser_ports:              #turn lasers on
                            GPIO.output(laser, int(laser_trials[trial]))
                            print('Lick detected, Laser is turned ON')
                            time.sleep(trial_duration)
                        for laser in laser_ports:              #turn lasers off
                            GPIO.output(laser, 0)
                            print('Laser is turned OFF')
                            time.sleep(ITI*0.8) #Wait for 80% of the ITI before looking for the shutter to open again
                    else:
                        print('Lick detected, Laser remains OFF for control trial')
                        time.sleep(trial_duration)
                        time.sleep(ITI*0.8) #Wait for 80% of the ITI before looking for the shutter to open again
                else:
                    print("Trial " + str(trial) + " expired: no lick detected")
                    time.sleep(ITI*0.8) #Wait for 80% of the ITI before looking for the shutter to open again

#%%
#Counts the #of loops passed until a high level of light is sensed
def rc_time(Lick_inport, maxWait, time_trial_start):
    r'''
    A sub-function of laser_trigger_all() that is triggered when the shutter opens, and monitors the lick sensor channel for the 1st lick in order to trigger the laser.

    :param int Lick_inport: A single value giving the IO pin on the Pi that recieves input from the lick sensor
    :param int maxWait: A single value giving the max wait time between shutter opening and 1st lick
    :param int time_trial_start: A single value giving the saved system time value from the start of the trial, for time keeping
    :return int count: A single value giving the number of loops between shutter opening and 1st lick, or 0 if the max wait time expires
    '''
    #Reset the counter
    count = 0
  
    #Initialize the lick sensor channel
    GPIO.setup(Lick_inport, GPIO.OUT) #Set the pin to output
    GPIO.output(Lick_inport, GPIO.LOW) #Set the output to LOW
    time.sleep(0.1) #Wait for the pin to adjust
    GPIO.setup(Lick_inport, GPIO.IN) #Change the pin back to input
  
    #Count until the pin goes high
    while (GPIO.input(Lick_inport) == GPIO.LOW):
        count += 1

        #Exit if the trial time limit expires
        if (time.time() - time_trial_start) >= maxWait: 
            return 0
    return count