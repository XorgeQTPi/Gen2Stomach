#!/ust/bin.python
import re 
'''
    This program will initialize a peristaltic pump from ATLAS scientific
    if a raspberry pi
    Author: JOSHUA MADSEN
    DATE: 12/14/18
    Edited: 2/1/19
'''


from AtlasI2C_ver2 import AtlasI2C
from AtlasError import *

class pump(AtlasI2C):
    
    errorOptions = {
                 '2' : AtlasSyntaxError,
                 '254' : AtlasTimeError,
                 '255' : AtlasNoDataError
                   }
    
    def __init__ (self, address,curVol = 0 ,bus = 1):
        super().__init__(address,bus)
        self.volume = curVol

    def setDispensed(self,mL):
        self.volume = mL
        
    def blink(self):
        passFlag = False
        while not passFlag:
            try :
                super().write('find')
                passFlag = True
            except:
                passFlag = False

    def checkDispensed(self)  -> float:
        passFlag = False
        while not passFlag:
            try :
                reading = super().query('R')
                passFlag = True
            except:
                passFlag = False
        if not reading[0]:
            raise(pump.errorOptions[reading[1]])
        else:
            return float(reading[1])

    def dispense(self, volume,time = ''):
        # give volume in mL
        # give time in minutes
        volume = round(int(volume))
        if time == '':
            response = super().query('D,'+str(volume))
        else:
            response = super().query('D,'+str(volume)+','+str(time))

        if not response[0]:
            print('error, Volume = '+str(volume)+ ': time = ' +str(time))
            raise(pump.errorOptions[response[1]])
        else:
            self.volume = self.volume + volume
            return (response[1])
            
    def check_total(self) -> float: # need to parse out '?TV,'
        response = super().query('TV,?')
        if not response[0]:
            print (pump.errorOptions[reading[1]])    
        #response = response[1].rstrip('\x00') # <- recent change
        else:
            stringResponse = response[1]
            splitResponse = stringResponse.split(',')
            return float(splitResponse[1])
        
    def clear_total(self):
        response = super().query('clear')
        if not response[0]:
            raise(pump.errorOptions[response[1]])
        else:
            return response[1]

    def calibrate(self,volume):
        response = super().query('CAL,'+str(volume))
        if not response[0]:
            raise(pump.errorOptions[response[1]])
        else:
            return response[1]

    def getMaxRate(self):
        response = super().query('DC,?')
        if not response[0]:
            raise pump.errorOptions['2']
        else:
            return float(response[1][response[1].find(',')+1:])



if  __name__ == '__main__':


    pass_flag = False
    
    testPump = pump(103,1)
    while pass_flag == False:
        testPump.blink()
        yes_no = input('Is it blinking [y/n]?')
        if yes_no.upper() == 'Y':
            path = input('type C for calibration, R for read, or D for dispense')
            if path.upper() == 'C':
                cal_type = input('What volume was given; or clear ; or ?')
                print(testPump.calibrate(cal_type))
            elif path.upper() =='R':
                print(testPump.checkDispensed())

            elif path.upper() == 'D':
                volume = input('How much to dispense? (volume in mL) ')
                print(testPump.dispense(volume))
            else:
                pass_flag = False
                                 
            

























    
