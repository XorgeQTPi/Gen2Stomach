import equations_for_stomach as eq
import numpy as np
import matplotlib.pyplot as plt


plt.ion()

start_stop = [6*60*60, 6*60*60+30*60]
#start_stop = [4*60*60,5*60*60]
feed_rate = [500,0]#,.2,0]
#feed_rate = [int(300/1000),0]
sched = [0,6*60*60,6*60*60,6*60*60+30*60,6*60*60+30*60,24*60*60]



sched_rate = [0,0,300,300,0,0]

A = eq.stomachTargets(start_stop,feed_rate)

vol = A.VolumeTarget
ph = A.pHTarget

time = [0]*len(vol)
for i in range(len(vol)):
    time[i] = i

pHImpulseTime = np.arange(0,86400)
pHImpulse = A.pHFun(pHImpulseTime)

fig, axs = plt.subplots(4,1)
axs[0].plot(time,vol)#,sched,sched_rate)
axs[0].grid(True)

axs[1].plot(time,ph)#,sched,sched_rate)
axs[1].set_ylabel('ph')
axs[1].grid(True)

axs[2].plot(time,A.moleTarget)
axs[2].set_ylabel('moles')
axs[2].grid(True)

axs[3].plot(sched,sched_rate)
axs[3].set_ylabel('sched')
axs[3].grid(True)
p = plt.axvspan(60, 60000, facecolor='#2ca02c', alpha=0.5)

plt.axis([0,24*60*60,0,max(sched_rate)*1.25])
fig.tight_layout()

plt.show()


fig, axs = plt.subplots(4,1)
axs[0].plot(time,vol)#,sched,sched_rate)
axs[0].grid(True)

axs[1].plot(time,ph)#,sched,sched_rate)
axs[1].set_ylabel('ph')
axs[1].grid(True)

axs[2].plot(time,A.moleTarget)
axs[2].set_ylabel('moles')
axs[2].grid(True)

axs[3].plot(sched,sched_rate)
axs[3].set_ylabel('sched')
axs[3].grid(True)
p = plt.axvspan(600, 60000, facecolor='#2ca02c', alpha=0.5)

plt.show()

