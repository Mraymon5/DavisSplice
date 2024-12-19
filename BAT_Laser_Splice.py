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
import ast
#import sys

#%% Setup
# Setup pi board
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

#define the pin that goes to the beam break for shutter open/close detection
Shutter_inport = 5
#define the pin that goes to the lick detector (the photodiode)
Lick_inport = 7

#%% Laser Trigger Function, for laser on every trial            
def laser_trigger_all(laser_ports = [16,12], #Pins that output to the laser
                      trial_duration = 5, #Trial Duration (sec)
                      NTrials = None, #Number of trials in session
                      subj_id = None, #Subject ID
                      maxWait = 60, #Max Wait time per trial (sec)
                      ITI = 10, #Inter-Trial Interval (sec)
                      Shutter_inport = 20, #Pin monitoring the shutter mag sensor
                      Lick_inport = 21): #Pin monitoring the lick sensor
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
    
    #Set up shutter input pin
    GPIO.setup(Shutter_inport, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    #Set up the lick input pin
    GPIO.setup(Lick_inport, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #Change the pin back to input

    #Get user inputs if they have not been provided
    Params = easygui.multenterbox(title= 'Parameters',
                                  fields=["Subject ID","Laser output ports", "Shutter input Port", "Lick input port","Trial duration", "N Trials", "Max Wait", "ITI"],
                                  values=[subj_id,laser_ports,Shutter_inport,Lick_inport,trial_duration,NTrials,maxWait,ITI])
    subj_id = str(Params[0])
    laser_ports = ast.literal_eval(Params[1])
    Shutter_inport = int(Params[2])
    Lick_inport = int(Params[3])
    trial_duration = int(Params[4])
    NTrials = int(Params[5])
    maxWait = int(Params[6])
    ITI = int(Params[7])
    print(Params)

    if not NTrials:
        taste_seq = easygui.multenterbox(msg = 'Enter the number of taste presentations:', 
                                         fields = ['Number of Trials'])
        taste_seq = taste_seq[0].split(',')
        NTrials = int(taste_seq[0])
    while subj_id == '':
        subj_id = easygui.multenterbox(msg = 'Enter the animal ID:', fields = ['Animal ID'])[0]
    if subj_id is None:
        print("Exiting")
        return
    
    #create laser order for each taste
    laser_trials = np.ones(NTrials)

    print("Number of trials: " + str(NTrials))
    print("Laser Sequence: " + str(laser_trials))

    #Save laser trial order into a text file
    with open("{}_trials_order_{}.txt".format(subj_id[0],time.strftime("%Y%m%d")), 'w') as laserfile:
        OutText = "Animal_ID,NTrials,StartTime" + "\n" + str(subj_id) + "," + str(NTrials) + "," + str(time.strftime("%H:%M:%S"))
        laserfile.write(OutText)

    print('Press Ctrl-C to quit!')

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
                        print('Lick detected, Laser ON')
                        time.sleep(trial_duration)
                        for laser in laser_ports:              #turn lasers off
                            GPIO.output(laser, 0)
                        print('Trial Elapsed, Laser OFF')
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
  
    #Count until the pin goes high
    while (GPIO.input(Lick_inport) == GPIO.LOW):
        count += 1

        #Exit if the trial time limit expires
        if (time.time() - time_trial_start) >= maxWait: 
            return 0
    return count

#%%
if __name__ == "__main__":
    laser_trigger_all()
