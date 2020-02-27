import numpy as np
import math

# Author Joshua Madsen
# Discription
# edited 3/30
# added self.moleTarget
''' A class with static methods to hold the arrays for ideal pH and Volume status
each array index corresponds to a single second as it currently stands.
The entire creation takes about 5 minutes, thus it is desireable to create a class
that serves as in inbetween from seconds to index values that will be created in the current
simulated_stomach module'''

class stomachTargets:
    
    def __init__(self,start_stop,feed_rate,volTime = 86400, pHtime = 86400):
        self.VolumeTarget = stomachTargets.getConvolvedVol(start_stop,feed_rate,volTime, 40)
        print('gotVolume')
        #self.pHTarget = stomachTargets.getConvolvedpH(start_stop,pHtime)
        self.pHTarget = stomachTargets.getSlidpH(start_stop,pHtime)
        print('got pH')
        concentration = [10**(-1*x) for x in self.pHTarget]
        self.moleTarget = list(map(lambda x,y:x*y,concentration,self.VolumeTarget))
        
    @staticmethod    
    def pHFun(second):
        ans=[]
        a0 = 2.373;
        a1 = 0.5717;
        a2 = 0.09359;
        a3 = -0.03781;
        a4 = -0.1185;
        a5 = -0.08821;


        b1 = 0.875;
        b2 = 0.6021;
        b3 = 0.3727;
        b4 = 0.2654;
        b5 = 0.08344;
        w = 0.0004059;

        for i in np.nditer(second):
            if i<15206:
                k = i-1500
                ph = a0 + a1*math.cos(k*w)+b1*math.sin(k*w)+a2*math.cos(k*w*2)+b2*math.sin(k*w*2)+a3*math.cos(3*w*k)+b3*math.sin(3*w*k)+a4*math.cos(4*w*k)+b4*math.sin(4*w*k)+a5*math.cos(5*w*k)+b5*math.sin(5*w*k)
                ans.append(ph)
            else:
                ans.append(1.51)
        return ans
        '''#right now return concentrations
        ans = []
        #return concentration of hydrogen+
        change = 4000
        # all times before 4000 seconds are plotted with gausian
        # after are plotted with fourier 
        a1 = 2.318
        b1 = 913.9
        c1 = 539.6

        a2 = 1.968
        b2 = 1979
        c2 = 1169

        a3 = .6987
        b3 = 4341
        c3 = 1747

        a4 = 1.991
        b4 = -284.8
        c4 = 27870

        A0 = 1.935
        A1 = -0.2639
        A2 = -0.2104
        A3 = 0.05719

        B1 = 0.3706
        B2 = -0.1241
        B3 = -0.1176
        W = 0.0004525
            
        def gausian(a,b,c,x):
            return a*math.exp(-((x-b)/c)**2)

        for i in np.nditer(second):
            

            #return np.piecewise(second,[second<change, second <14580],[gausian(a1,b1,c1,second)+gausian(a2,b2,c2,second)+gausian(a3,b3,c3,second)+gausian(a4,b4,c4,second),A0 + A1*math.cos(second*W)+B1*math.sin(second*W)+A2*math.cos(second*W*2)+B2*math.sin(second*W*2)+A3*math.cos(3*W*second)+B3*math.sin(3*W*second),1.513])


            if i< change:
                ph = gausian(a1,b1,c1,i)+gausian(a2,b2,c2,i)+gausian(a3,b3,c3,i)+gausian(a4,b4,c4,i)
            if i < 14580:
                ph = A0 + A1*math.cos(i*W)+B1*math.sin(i*W)+A2*math.cos(i*W*2)+B2*math.sin(i*W*2)+A3*math.cos(3*W*i)+B3*math.sin(3*W*i)
            else: # steady state value, this is close to continuous with the current function
                ph = 1.513
            #ans.append(10**(-ph))
            ans.append(ph)
        return ans
        '''

        
    @staticmethod    
    def volFun(second):
        ml = 2**(-(second/(30*60))**.8)
        return ml


    @staticmethod
    def getConvolvedVol(start_stop,feed_rate,sample_time = 200*60,minVol = 40):
        # start stop stores times since midnight in seconds
        # feed rate stores vol rates in ml/Hr
        # sample time is in seconds and is the length of window to convolve over

        
        volImpulseTime = np.arange(0,sample_time)
        volImpulse = stomachTargets.volFun(volImpulseTime)
        prev = 0
        schedule = []
        for i in range(0,len(start_stop),2):
            lengthOff = start_stop[i]-prev
            schedule = schedule+([feed_rate[i+1]]*lengthOff)
            prev = start_stop[i+1]
            lengthOn = prev - start_stop[i]
            schedule = schedule + ([feed_rate[i]]*lengthOn)
        if len(schedule) < 24*60*60:
            schedule = schedule + [0]*(24*60*60-len(schedule))
        # should add the minimum amount to every value below a threshold before returning
        VOL = np.convolve(np.ravel(schedule),volImpulse,'full')
        VOL2 = [x+minVol for x in VOL]
        return VOL2[0:24*60*60]
        #return schedule
    @staticmethod
    def getConvolvedpH(start_stop,sample_time = 14890):
        # not confident that this is physiologically relavent becasue the
        # stomach should compensate for events like continous feeding
        maxpH = 5
        schedule = []
        pHImpulseTime = np.arange(0,sample_time)
        pHImpulse = stomachTargets.pHFun(pHImpulseTime)
        prev = 0
        for i in range(0,len(start_stop),2):
            lengthOff = start_stop[i]-prev
            schedule = schedule+([0]*lengthOff)
            prev = start_stop[i+1]
            lengthOn = prev - start_stop[i]
            schedule = schedule + ([1]*lengthOn)
        if len(schedule)<24*60*60:
            schedule = schedule + [0]*(24*60*60-len(schedule))
        concentration = np.convolve(np.ravel(schedule),pHImpulse,'full')

    #    for i in concentration:
    #        i = -math.log(i,10)
        #concentration = list(map(lambda x: x if x <= 6 else maxpH,concentration))
        # ^^ cut off portion of function keeps everything under maxpH
                 
        concentration = concentration[0:24*60*60]
        return concentration

    def getSlidpH(start_stop, sample_time = 14890):
        
        schedule = []
        pHImpulseTime = np.arange(0,sample_time)
        pHImpulse = stomachTargets.pHFun(pHImpulseTime)
        prev = 0
        for i in range(0,len(start_stop),2):
            lengthOff = start_stop[i]-prev
            schedule = schedule+([0]*lengthOff)
            prev = start_stop[i+1]
            lengthOn = prev - start_stop[i]
            schedule = schedule + ([1]*lengthOn)
        if len(schedule)<24*60*60:
            schedule = schedule + [0]*(24*60*60-len(schedule))

        steady = [1.51]*60*60*24
        try:
            for i in range(len(schedule)):
                if schedule[i] != 0:
                    for k in range(i,len(schedule)):
                        if steady[k]<pHImpulse[k-i]:
                            steady[k] = pHImpulse[k-i]

        except IndexError as e:
            print(str(len(steady))+' : '+ str(len(pHImpulse)) + ' : ' +str(k))
            
                  
        return steady[0:24*60*60]

















    
