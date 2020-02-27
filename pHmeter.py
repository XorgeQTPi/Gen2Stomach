#!/ust/bin.''' this program will initialize a pH meter for ATLAS
#    Author: Joshua Madsen
#    Date: 11/30/18
#    edited: 1/2/18
    


from AtlasI2C_ver2 import AtlasI2C
from AtlasError import*



class pHmeter(AtlasI2C):
    calOptions = {  'LOW' : 'Cal,LOW,4.00',
                'MID' : 'Cal,MID,7.00',
                'HIGH' : 'Cal,HIGH,10.00',
                'CLEAR' : 'Cal,CLEAR',
                '?' : 'Cal,?'
                }
    errorOptions = { '2' : AtlasSyntaxError,
                 '254' : AtlasTimeError,
                 '255' : AtlasNoDataError
                }
    # current address

    def __init__(self, address, bus = 1):
        super().__init__(address,bus)      
        # initializes I2C to either a user specified or default address
        # self.set_i2c_address(address)

    def checkpH(self):
        passFlag = False
        while not passFlag:
            try :
                tupleReading = super().query('R')
                passFlag = True
            except:
                passFlag = False
        if tupleReading[0] == False:
            raise pHmeter.errorOptions[reading[1]]()
        else :
        #reading = reading.rstrip('\x00') # <- recent change # not needed added in AtlasI2C
            return float(tupleReading[1])

    def blink(self):
        passFlag = False
        while not passFlag:
            try :
                super().write('find')
                passFlag = True
            except:
                passFlag = False
        
    def calibrate(self,string) -> str :
        if isinstance(string,str):
            string=string.upper()
            try:
                response = super().query(pHmeter.calOptions[string])

            except(KeyError):
                print('not a valid option for calibration. \'?\' selected')
                response = super().query(pHmeter.calOptions['?'])

        else:
            return 'Failed Calibration'

        return response[1]


if  __name__ == '__main__':


    pass_flag = False
    
    ph = pHmeter(99,1)
    while pass_flag == False:
        ph.blink()
        yes_no = input('Is it blinking [y/n]?')
        if yes_no.upper() == 'Y':
            path = input('type C for calibration or R for read')
            if path.upper() == 'C':
                cal_type = input('Calibration type: LOW, MID, HIGH, CLEAR, or ? : ')
                print(ph.calibrate(cal_type))
            elif path.upper() =='R':
                print(ph.checkpH())

            else:
                pass_flag = False
                                 



            
