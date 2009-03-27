#! /usr/bin/env python
"""
Computes hourly gains using autocorrelation given input galactic gain file 'auto.dat' and data file
zen.uvcb. Gain is averaged over a small range of frequencies that are nominally
RFI free.
158MHz with bw=0.35 works well at Green Bank.

Inputs
   galaxy file (--gal_file=*.dat)
   data file *.uvcb
   frequency [MHz] (--freq=150)
   bandwidth [MHz] (--bw=0.35) 0.35 is one 1/256 channel
   Decimation,Ant,Pol
"""

import aipy as a, numpy as n, pylab as p, math as m, sys
import optparse,cPickle,pprint

o = optparse.OptionParser()
o.set_usage('gain_track.py [options] *.uv')
o.set_description(__doc__)
o.add_option('--gal_file',dest='gal_file_name',
             help="""A file containing average galaxy response in .dat (pickled)
             format.""")
o.add_option('--freq',dest='freq',
             help="""Frequency in MHz. This will be the lower edge of the
             band.""")
o.add_option('--bw',dest='bw',
             help="""Bandwidth in MHz.""")
a.scripting.add_standard_options(o,dec=True,pol=True,loc=True)
opts, args = o.parse_args(sys.argv[1:])
"""
Steps:
    0) Load galaxy file.
    1) Cycle through data files.
       2) Average over freq.
       3) Average into 1 hour bins 
       4) Divide by galaxy data.
       5) Save point, continue
    6) Save pickle
    7) Plot.
"""
#Load pickled galaxy file.
gal_file = open(opts.gal_file_name,'rb')
dda = cPickle.load(gal_file)
gal_file.close()
times = n.array(dda.keys())
#load nicole's Haslam*beam model
hfile = open("model_142.txt",'r')
has = []
for line in hfile:
    if not line.startswith('FORPRINT'):
        has.append(map(float,line.split()))
has = n.array(has)

#compute desired channels
opts.bw = float(opts.bw)/10**6 #convert to GHz
uv = a.miriad.UV(args[0])
chan = str(str(round((float(opts.freq)-
            float(uv['sfreq']))/float(uv['sdf']))).split('.')[0]+','+
         str(round((float(opts.freq)+float(opts.bw)-
                    float(uv['sfreq']))/float(uv['sdf']))).split('.')[0])
del(uv)
print "using channels", chan
A = {}
for file in args:
    print "loading file :",file
    sys.stdout.flush()
    uv = a.miriad.UV(file)
    aa = a.loc.get_aa(opts.loc, uv['sdf'], uv['sfreq'], uv['nchan'])
    chans = a.scripting.parse_chans(chan,uv['nchan']) 
    a.scripting.uv_selector(uv,'auto', opts.pol)
    uv.select('decimate',opts.decimate,opts.decphs)

    D = {}
    t_min =0
    for (uvw,t,(i,j)),d in uv.all():
        if t_min==0:
            t_min=t
        d = n.ma.compressed(d.take(chans))
        d = n.abs(d.sum()/len(d))
        if not D.has_key(i): D[i] = [0]
        D[i].append(d)
    aa.date = a.ant.juldate2ephem((t+t_min)/2) #the center of the bin 
    for k in D.keys():
        D[k] = n.mean(D[k])
    #the nearest curent sidereal time
    ts = n.where(abs(times-aa.sidereal_time())==n.min(abs(times-aa.sidereal_time())),
                 times,0).sum()
    for j in D.keys():
        if not A.has_key(j): A[j]={}
        A[j][float(aa.date)] = [D[j], dda[ts][0], dda[ts][1],
                                n.where(abs(has[:,0]-aa.sidereal_time()*12/n.pi)==n.min(abs(has[:,0]-aa.sidereal_time()*12/n.pi)),
                                        has[:,1],0).sum()]
        # pprint.pprint(A[j])
#pprint.pprint(D[1])
#pprint.pprint(A[1])
#p.plot(A[1].keys(),A[1].values(),'.')
#p.show()
gainfile = open('gains.dat','wb')
cPickle.dump(A,gainfile)
gainfile.close()
m2 = int(m.sqrt(len(n.array(A.keys()))))
m1 = int(m.ceil(len(n.array(A.keys()))/m2))
for k in A.keys():
    print m2,m1,int(k)+1
    p.subplot(m1,m2,int(k)+1)
    p.plot(A[k].keys(),A[k].values(),'.')
p.show()

