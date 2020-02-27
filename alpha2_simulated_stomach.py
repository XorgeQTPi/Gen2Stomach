#!/ust/bin/python
#import AtlasI2C_ver2


'''
Author: Joshua Madsen
Senior Design project: SLU and Cardinal Health
The goal of this program is to control 3 pumps and read pH from from a pH probe.
pH and volume are combined to determine the number of H+ ions.
The number and total volume is then passed into a PID loop which determines the actions
necessary to correct the system.


April 5 2019: Edited code to add acid and add buffer
edited helper function to activate pumps to also return a boolean based on volume
April 13 2019: Pumps now run 5 seconds after end of previous run. the pause time between functions is variable now
April 16 2019: Converted pumpRate -> mL /s

'''
import bisect
import datetime
import sys
import json
import os
import threading
import time

import pump
import pHmeter
import equations_for_stomach as eq
import TESTpump
import PID2
import updatingGraph


class stomachTest:

    def __init__(self,name: str,mode: bool):
        # name is a string to be used when creating the state file
        #self.setupComponents()
        ####
        self.VerboseTest = open("alphaVerboseTestApril29.txt","w")
        self.pumpWaste = pump.pump(105)
        self.pumpBuffer = pump.pump(104)
        self.pumpAcid = pump.pump(103)
        self.probe =pHmeter.pHmeter(99)

        self.pumpRate = min([self.pumpAcid.getMaxRate(),self.pumpAcid.getMaxRate(),self.pumpAcid.getMaxRate()])
        self.pumpRate = self.pumpRate/60 # convert from mL/min -> mL/sec


        self.resumeFileName = name

        self.mode = mode

        self.start_stop = []
        self.feed_rate = []
        self.numDays = 0
        self.start_time = None
        self.end_time = None 
        # Acid, Buffer, Feed in mL
        self.runningVol = [40, 0, 0];# add into automated section and user input
        self.pumpAcid.setDispensed(40)
        self.lastFedVol = 0;

        self.readingName = 'april29data.txt'
        
    @classmethod
    def restart(cls,file):
        return cls(name,False)

    '''
    def midnight(self): #dont think this is needed anymore but leaving it in case
        theading.Timer(24*60*60,midnight).start()
        # need to reset amount of fluid pumped by each pump
        self.pumpWaste.clear()
        self.pumpBuffer.clear()
        self.pumpAcid.clear()
    '''

    def getInput(self):
        # two methods for getting input
        # 1. is from a file requires mode to be False. file in json format
        # 2. is from a series of text based user prompts eventually to be replaced with a GUI
        if self.mode == False:
            # read inputs from file
            recoveryFile = open(self.resumeFileName,'r')
            recoveryArray = json.load(recoveryFile)
            recoverFile.close()
            self.start_time = datetime.datetime.strptime(recoverArray[0],'%Y-%m-%d %H:%M:%S.%f')#    [start_time,end_time,curTime,feed_rate,start_stop,userStart]
            self.end_time = datetime.datetime.strptime(recoveryArray[1],'%Y-%m-%d %H:%M:%S.%f')
            curTime = datetime.datetime.strptime(recoveryArray[2],'%Y-%m-%d %H:%M:%S.%f')
            self.feed_rate = recoverArray[3]
            self.start_stop = recoverArray[4]
            self.pumpAcid.volume = recoverArray[5]
            self.pumpBase.volume = recoverArray[6]
            self.pumpWaste.volume = recoverArray[7]
            
        else:
            # user entry and error checking
            userStart = True
            numFeed = input('How many feedings per day? ')
            numDays = input('How many days should this test run for? ')
            self.start_time = datetime.datetime.now()
            try:
                int(numDays)
            except TypeError:
                print(' Invalid number entered ' )
                print('default number of days = 10')
                numDays = '10'
            self.end_time = self.start_time + datetime.timedelta(days = int(numDays))            
            passFlag = False
            while (passFlag == False):

                if( numFeed.isdecimal() and numDays.isdecimal()) and int(numFeed)<86400 and int(numDays)<1000:
                    numFeed = int(numFeed)
                    numDays = int(self.numDays)
                    passFlag = True
                    
                else:
                    print("User entered value was not correct please enter a number")
                    numFeed = input('How many feedings per day? ')
                    numDays = input('How many days should this test run for? ')
            passFlag = False
            i =1

            while (passFlag == False):

                while i <=numFeed:
                    print('enter values as hh:mm')
                    x = input('When should feeding '+str(i)+' start? ')
                    y = input('When should feeding '+str(i)+' end? ')
                    rate = input('What is the rate for this feeding in mL/h? ')

                    if x.find(":") and y.find(":") == 2 and rate.isdecimal():  
                        xParse = x.split(':')
                        yParse = y.split(':')
                        rate = float(rate)
                        rate = rate/(60*60)
                        
                        if (len(xParse)==2 and len(yParse)==2):
                            xHour = xParse[0]
                            xMin = xParse[1]
                            yHour = yParse[0]
                            yMin = yParse[1]

                            if( xHour.isdecimal() and xMin.isdecimal() and yHour.isdecimal() and yMin.isdigit()):
                                xHour = int(xHour)
                                xMin = int(xMin)
                                yHour = int(yHour)
                                yMin = int(yMin)

                                if (xHour<24 and xHour>=0 and yHour<24 and yHour>=0 and xMin>=0 and xMin<60 and yMin>= 0 and yMin<60 and (yHour*60+yMin)>(xHour*60+xMin)):
                                    i+=1
                                    passFlag = True
                                    xSeconds = ((60*xHour)+xMin)*60
                                    ySeconds = ((60*yHour)+yMin)*60
                                    self.start_stop.append(xSeconds)
                                    self.start_stop.append(ySeconds)
                                    self.feed_rate.append(rate)
                                    self.feed_rate.append(0)

                                else:
                                    print("User entered values were not correct. Please ensure the end time is greater than start time and that the minutes and hours conform to standard practice.")
                            else:
                                print("User entered value was not correct please enter a number.")
                        else:
                            print("The user input was incorrect. Please enter in hh:mm form.")
                    else:
                        print("The user input was incorrect. Please enter in hh:mm form.")

    def saveState(self,curTime):
        # removes an existing file is applicable and creates a new one with the save state variables required to restart run
        try:
            os.remove(self.resumeFileName)

        except OSError:
            pass
        
        saveStateArray = [str(self.start_time),str(self.end_time),str(curTime),self.feed_rate,self.start_stop,self.pumpAcid.volume,self.pumpBuffer.volume ,self.pumpWaste.volume ]
        resumeFile = open(self.resumeFileName,'w')
        json.dump(saveStateArray,resumeFile)
        resumeFile.close()

    def setupComponents(self):
        print ('Please make sure that the components are are I2C mode before continuing.')
        self.pumpWaste = pump.pump(105)
        self.pumpBuffer = pump.pump(104)
        self.pumpAcid = pump.pump(103)
        self.probe =pHmeter.pHmeter(99)
        print('If at any time you would like to cancel please press ctrl-c.')
        passFlag = False

        while passFlag == False:
            self.pumpAcid.blink()
            acidBool = input('Type yes if only the acid pump is blinking: ')
            
            if acidBool.upper().startswith('Y'):
                self.pumpAcid.check_total()
                self.pumpBuffer.blink()
                baseBool = ('Type yes if only the base pump is blinking: ')

                if baseBool.upper().startswith('Y'):
                    self.pumpBuffer.check_total()
                    self.pumpWaste.blink()
                    wasteBool = input('Type yes if only the waste pump is blinking: ')

                    if wasteBool.upper().startswith('Y'):
                        self.pumpWaste.check_total()
                        print('The pumps are set up correctly.')
                        self.probe.blink()
                        probeBool = input('Type yes if only the pH probe board is blinking: ')

                        if probeBool.upper().statswith('Y'):
                            self.probe.checkpH()
                            print('The components are set up correctly.')
                            passFlag = True

                        else: # probe wrong
                            print('Please disconnect the power from the other elements (if any) that were blinking.')
                            userChange = input('If you know the address of the pH probe, please enter it in base 10 forma:')
                            invalid = True
                            
                            while invalid:

                                try:
                                    int(userChange)
                                    self.probe.set_i2c_address(int(userChange))
                                    invalid = False

                                except:
                                    print('That was not a valid input, please try again.')

                    else: #waste wrong
                        print('Please disconnect the power from the other elements (if any) that were blinking.')
                        userChange = input('If you know the address of the waste pump, please enter it in base 10:')
                        invalid = True

                        while invalid:

                            try:
                                int(userChange)
                                self.pumpWaste.set_i2c_address(int(userChange))
                                invalid = False

                            except:
                                print('That was not a valid input, please try again.')

                else: #base wrong
                    print('Please disconnect the power from the other elements (if any) that were blinking.')
                    userChange = input('If you know the address of the buffer pump, please enter it in base 10 format: ')
                    invalid = True

                    while invalid:

                        try:
                            int(userChange)
                            self.pumpBuffer.set_i2c_address(int(userChange))
                            invalid = False

                        except:
                            print('That was not a valid input, please try again.')
                            
            else: # acid wrong
                print('Please disconnect the power from the other elements (if any) that were blinking.')
                userChange = input('If you know the address of the acid pump please enter it in base 10 format: ')
                invalid = True

                while invalid:

                    try:
                        int(userChange)
                        self.pumpAcid.set_i2c_address(int(userChange))
                        invalid = False

                    except:
                        print('That was not a valid input, please try again.')

    def getFedVolume(self,time_since_midnight) -> int:
        # returns the volume of formula that should have been administered by the feeding tube
        #based on time and the feeding schedule for a single day
        #created 12/17 updated 12/29
        # linear interpolation
        pos = bisect.bisect(self.start_stop,time_since_midnight)
        volume = 0
        i = 0

        while i < pos-(pos%2):
            delta=self.start_stop[i+1]-self.start_stop[i]
            volume = volume + delta*self.feed_rate[i]
            i = i+2

        if pos%2 == 1:
            delta=time_since_midnight-self.start_stop[i]
            volume = volume +delta*self.feed_rate[i]

        self.runningVol[2] = self.runningVol[2]+volume
        self.lastFedVol = volume
        return volume

    def checkVol(self,time_since_midnight):
        # each second corresponds to the array index of that value
        # uses the values from the pumps and what the value is supposed to be from the feeding tube
        # to determine the current volume
        # created 12/17 updated 1/8
        # sums feedPump, acidPump, bufferPump and subtracts wastepump values to determine actual volume
        PV = self.getFedVolume(time_since_midnight)
        AV = stomachTest.calcPumpVolume(self.pumpAcid)
        BV = stomachTest.calcPumpVolume(self.pumpBuffer)
        WV = stomachTest.calcPumpVolume(self.pumpWaste)
        return PV+AV+BV-WV

    def checkpH(self):
        '''Added for more readability. No different from probe.checkpH()'''
        # tested
        return (self.probe.checkpH())
    
    def addAcid(self,mL):
        # added for readability
        # Pumps dont run unless .5mL of fluid are added
        flag = stomachTest.__pumpVolume(self.pumpAcid,mL)
        if flag == True:
            self.runningVol[0] = self.runningVol[0]+mL
        pass
    
    def addBuffer(self,mL):
        # added for readability
        # Pumps dont run unless .5mL of fluid are added
        flag = stomachTest.__pumpVolume(self.pumpBuffer,mL)
        if flag == True:
            self.runningVol[1] = self.runningVol[1]+mL
        pass

    # Make same as add buffer nd add acid
    def removeContents(self,mL):
        # added for readability
        # uses waste pump to remove a set amount of volume
        stomachTest.__pumpVolume(self.pumpWaste,mL)
        totalvol = sum(self.runningVol)
        self.runningVol = [i-i*mL/totalvol for i in self.runningVol] # Removes all parts of stomach assuming fully mixed
        pass
    
    @staticmethod 
    def __pumpVolume(pump,amount,time = ''):
        #NOTE returns a boolean and preforms a state change and a physical change 
        if abs(amount) <.5:
            return False
        else:
            pump.dispense(amount,time)
            return True
    
    @staticmethod    
    def calcPumpVolume(pump): # This is a separate method because might still need to reset at midnight or reset at some point and split the storage of the date
        return pump.volume # I wonder if there should be checks and balances on the on this?
        
    def main(self):

        testCase = True
        if testCase:
            print('Starting Main of alpha_simulated_stomach')
        equations = eq.stomachTargets(self.start_stop,self.feed_rate) #using defaultsfound in equations for stomach 
        if testCase:
            print('Equations have been created.')
        if testCase:
            print('Entering While loop...')


        display = updatingGraph.updatingGraph(equations.VolumeTarget,equations.pHTarget,equations.moleTarget,self.start_stop,self.feed_rate)
        control = PID2.PID2(maxVol = 1000)
        control.setAcceptedPhError(0.25)
        control.setKi(0)
        control.setKd(0)
        control.setKp(1.0)
  

        curTime = datetime.datetime.now()
        while curTime < self.end_time:
            secSinceMid = (curTime.hour*60+curTime.minute)*60+curTime.second # convert time to seconds from midnight used in array access
            curPh = self.checkpH() 
            curVol = self.checkVol(secSinceMid)
            setVol = equations.VolumeTarget[secSinceMid]
            setMole = equations.moleTarget[secSinceMid]/1000
            

            command=control.getCommand(setVol,setMole,curVol,curPh)

            #Waste 
            if command[2] > 0: 
                self.removeContents(command[2])
                
            #Acid
            if command[0] > 0:
                self.addAcid(command[0])

            #Buffer
            if command[1] > 0:
                self.addBuffer(command[1])


            statestr = str(secSinceMid)+','+str(command)+','+str(curVol) +',' +str(setVol) +',' +str(curPh)+'\n'
            with open(self.readingName, 'a+') as f:
                f.write(statestr)

            display.update(curVol,curPh,10**(-1*curPh)/1000*curVol,secSinceMid)
            time.sleep((max(command)/self.pumpRate)+5)

            if testCase:
                self.VerboseTest.write(str(secSinceMid)+','+str(command)+','+str(curVol) +',' +str(setVol) +',' + str(curPh)+ '\n')

            
            self.saveState(curTime)
            curTime = curTime.now()

        self.VerboseTest.close()
        
if __name__ == '__main__':
    case = stomachTest('test',True)
    case.getInput()
    case.main()
            


        
