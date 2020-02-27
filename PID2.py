'''
Author: Joshua Madsen
Date: 2/21/19
Goal: Create a crude PID system
    1) Able to use in alpha simulated stomach and future iterations
    2) utilize constant and variable set points
    3) store data
        3a) act on stored data to improve reponses
    4) Control 2 different inputs that have different effects and interactions
    5) Use default data as a start point for variable proportional responses
    6) Use moles of H+ ions as error

    Update Log
    4/8/19 - fixed unassignment issue in getCommand
    4/18/19 - commented out minimal value of acid to add

'''
import math
import bisect

class PID2:

    def __init__(self,**kwargs):
        """
        A class for controlling the pH and Volume of simulated Stomach based off of expirmental data points

        important keywords
        maxVol -> int that specifies tha maximum volume to be put into the stomach
        data -> string that specifies the location of the experimental data held in a CSV ordered
                Acid,Buffer,Feed,pH

        Attributes
        ----------
        VOLMAX : int
        #pRange : int
        Ki     : float
        Kd     : float
        
        Methods
        ----------
        __init__
        getAcceptedPhError() ->float
        setAcceptedPhError(float)
        setPRange(int)
        getPRange() ->int
        getCommand(self,setVol,setpH,curVol,curpH,composition)
        updateDataFile(string filename)
        
        staticMethods
        -------------
        distance(array1,array2)
        
        """
        
        #Files will contain the data for comparing pH based off of components
        self.arrayData = []
        
        if 'maxVol' in kwargs:
            self.VOLMAX = kwargs['maxVol']

        else:
            self.VOLMAX = 1000
        '''
        if 'data' in kwargs:
            dataFileName = kwargs['data']

        else:
            dataFileName = 'titrationfull.txt'

        self.updateDataFile(dataFileName)
        '''
##        with open(dataFileName, 'r') as f:
##            data = f.readlines()
##            for line in data:
##                line = line.rstrip('\n')
##                words = line.split(',')
##                arrayData.append(words)
##
##        for i in range(len(arrayData)): # will convert to float and normalize all of the volume measurements
##            for j in range(len(arrayData[i])):
##                arrayData[i][j] = float(arrayData[i][j])
##            indexsum = math.fsum(arrayData[i][0:3])
##            for k in range(len(arrayData[i])-1):
##                arrayData[i][k] = arrayData[i][k]/indexsum
##		
##        arrayData.sort(key = lambda x:PID.distance(x))
##
##        self.sortedDataFeedVol = sorted(arrayData, key = lambda x:x[2])    
##        self.sortedFeedVol = [row[2] for row in self.sortedDataFeedVol]
##        self.sortedpHVol = [row[3] for row in self.sortedDataFeedVol]
        '''self.pRange = 10''' # number of closes data points to look at

        self.Kp = 1
        self.Ki = .5
        self.Kd = .5
        self.acceptedErrorpH= 0.25
        self.pastError = []
        self.totalError = 0
    '''    
    @staticmethod
    def distance(array1,array2):
        if len(array1)!= len(array2):
            raise ValueError("list a and list b must have the same length")
        else:
            sumSquare = 0
            for i in range(len(array1)):
                sumSquare = sumSquare+ (array1[i]-array2[i])**2
        return sumSquare**.5
    
    def updateDataFile(self,fileName):
        arrayData =[]
        with open(fileName, 'r') as f:
            data = f.readlines()
            for line in data:
                line = line.rstrip('\n')
                words = line.split(',')
                arrayData.append(words)

        for i in range(len(arrayData)): # will convert to float and normalize all of the volume measurements
            for j in range(len(arrayData[i])):
                arrayData[i][j] = float(arrayData[i][j])
            indexsum = math.fsum(arrayData[i][0:3])
            for k in range(len(arrayData[i])-1):
                arrayData[i][k] = arrayData[i][k]/indexsum
		
        arrayData.sort(key = lambda x:PID.distance(x[0:3],[0,0,0]))

        self.sortedDataFeedVol = sorted(arrayData, key = lambda x:x[2])
        self.sortedFeedVol = [row[2] for row in self.sortedDataFeedVol]
        self.sortedpHVol = [row[3] for row in self.sortedDataFeedVol]
    '''

    
    def getAcceptedPhError(self):
        return self.acceptedErrorpH

    def setAcceptedPhError(self,pH):
        pH = float(pH)
        self.acceptedErrorpH = pH
    '''
    def setPRange(self,num):
        num = int(num)
        self.pRange = num

    def getPRange(self):
        return self.pRange
    '''
    def setKd(self,kd):
        self.Kd = kd

    def getKd(self):
        return self.Kd

    def setKi(self,ki):
        self.Ki = ki

    def getKi(self):
        return self.Ki

    def setKp(self,kp):
        self.Kp = kp

    def getKp(self):
        return self.Kp
            
    def getCommand(self,setVol,setMole,curVol,curpH):
        print('setVol: '+str(setVol) + 'setMole: ' + str(setMole) + 'curVol: ' + str(curVol) + 'curpH: ' +str(curpH) + '\n')
        #Cb -> COncentration of base [H+]
        #Ca -> Concentration of acid [H+]
        Cb = 10**(-7)/1000 # Should probably be variables 
        Ca = 10**(-1.512)/1000
        # going to check if within range
        acceptedErrorpH = self.acceptedErrorpH        
            
        curConc = (10**(-1*curpH))/1000
        curMole = curConc * curVol
        error = setMole - curMole
        self.pastError.append(error)

        workingVol = setVol - curVol
        # need to reduce volume if over

        response = self.P(error)+self.I(error)+self.D() # calculatePID loop response to error in terms of MOLES
        print(response)
        R = response
        Wv = workingVol
        Cc = curConc
        acidVol = 0
        baseVol = 0
        removeVol = 0
        
        if response <= 0 and workingVol <=0: # all numbers greater than 0 or too close to change
            print('case: 1')
            Vb = (R - Wv*Cc)/(Cb - Cc)
            Vr = (R - Wv*Cb)/(Cb - Cc)

            acidVol = 0
            baseVol = 0
            removeVol = 0
            if Vb >= 0 and Vr >=0:
                print('case: 1a')
                acidVol = 0
                baseVol = Vb
                removeVol = Vr

            Va = (R - Wv*Cc)/(Ca - Cc)
            Vr = (R - Wv*Ca)/(Ca - Cc)
            if Va >= 0 and Vr >= 0:
                print('case: 1b')
                acidVol = Va
                baseVol = 0
                removeVol = Vr

            Va = (R - Wv*Cb)/(Ca - Cb)
            Vb = (R - Wv*Ca)/(Cb - Ca)
            if Va >= 0 and Vb >= 0:
                print('case: 1c')
                acidVol = Va
                baseVol = Vb
                removeVol = 0
                
        elif response <= 0 and workingVol >=0:
            print('case: 2')
            frac = (R-Wv*Cb)/(curVol * Cb - curVol * Cc)
            
            if frac > 0 and frac <= 1:
                Vb = Wv + frac*curVol
                baseVol = Vb
                acidVol = 0
                removeVol = frac*curVol
            else:
                baseVol = 0
                acidVol = 0
                removeVol = 0                
                print('Response <= 0 & workingVol >=0, but frac<0 \n')

        elif response >= 0 and workingVol >= 0:
            print('case: 3')
            Va = (R - Wv*Cb)/(Ca - Cb)
            Vb = Wv - Va

            if Va > 0 and Vb >0:
                acidVol = Va
                baseVol = Vb
                removeVol = 0
            else:
                print('Va or Vb were negative but response > 0 and workVol > 0 \n')
                baseVol = 0
                acidVol = 0
                removeVol = 0

        elif response >= 0 and workingVol <= 0:
            print('case: 4')
            frac = (curMole + R - setVol*Ca)/(curMole - curVol*Ca)
            Va = setVol - curVol*frac
            if frac > 0 and Va > 0 and frac < 1:
                acidVol = Va
                baseVol = 0
                removeVol = (1-frac)*curVol
            else:
                print('frac < 0 or Va < 0 but response >0 and workVOl < 0 \n')
                baseVol = 0
                acidVol = 0
                removeVol = 0
                acidVol = response/Ca
                removeVol = acidVol - workingVol

        else:
            print('case: 5')
            print('None of the paths were taken, no change made')
            acidVol = 0
            baseVol = 0
            removeVol = 0
            
        #if acidVol > 0 and acidVol <0.5:
        #   acidVol = 5
        returnArray = [acidVol,baseVol,removeVol]
        print('command: ' + str(returnArray))
        if curVol < removeVol:
            print('removing more than total Volume')
        
        return(returnArray)

        
    def P(self,error):
        # error is positive if setState is more acidic
        # error is negative if the setState is more basic
    
        return self.Kp * error

    def I(self,error):
        # NOTE this could be sped up by only adding the last one every I=
        self.totalError = self.totalError+error
        if len(self.pastError) > 10:
            return self.totalError*self.Ki
        else:
            return 0

    def D(self):
        if len(self.pastError)>10:
            aveOld = sum(self.pastError[-8:-5])/3
            aveNew = sum(self.pastError[-3:])/3

            return (aveNew - aveOld)*self.Kd
        else:
            return 0
            





        
