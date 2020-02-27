import equations_for_stomach as eq
import numpy as np
import matplotlib.pyplot as plt


class updatingGraph:

    def __init__(self,volumeTarget,pHTarget,moleTarget,schedule,rate):
        plt.ion()
        self.time = list(range(0,len(volumeTarget)))
        self.volTar = volumeTarget
        self.pHTar = pHTarget
        self.moleTar = moleTarget
        self.sched = [0]
        self.rate = [0]*2
        for i in rate:
            self.rate.append(i)
            self.rate.append(i)
        
        for i in schedule:
            self.sched.append(i)
            self.sched.append(i)

        self.sched.append(24*60*60)

        self.plotTime = []
        self.plotVol = []
        self.plotPh = []
        self.plotMole = []

        self.fig, self.axs = plt.subplots(4,1)

        self.axs[0].plot(self.time,self.volTar,'r')#,sched,sched_rate)
        self.axs[0].grid(True)

        self.axs[1].plot(self.time,self.pHTar,'r')#,sched,sched_rate)
        self.axs[1].set_ylabel('pH')
        self.axs[1].grid(True)
        self.axs[2].plot(self.time,self.moleTar,'r')
        self.axs[2].set_ylabel('moles')
        self.axs[2].grid(True)

        self.axs[3].plot(self.sched,self.rate)
        self.axs[3].set_ylabel('sched')
        self.axs[3].grid(True)

        plt.axis([0,24*60*60,0,max(self.rate)*1.25])
        self.fig.tight_layout()
        plt.show()
        
    def update(self,curVol,curPh,curMole,time):
        
        self.plotTime.append(time)
        self.plotVol.append(curVol)
        self.plotPh.append(curPh)
        self.plotMole.append(curMole*1000)

        #fig, axs = plt.subplots(4,1)
        
        self.axs[0].plot(self.plotTime,self.plotVol,'b')
        
        self.axs[1].plot(self.plotTime,self.plotPh,'b')

        self.axs[2].plot(self.plotTime,self.plotMole,'b')


        p = plt.axvspan(0, time, facecolor='#2ca02c', alpha=0.5)


        self.fig.tight_layout()

        try:
            plt.draw()
            plt.pause(0.01)
        except _tkinter.TclError as e:
            print('Window was closed... Reopening')
            plt.show()
            plt.draw()
            plt.pause(0.01)


        
