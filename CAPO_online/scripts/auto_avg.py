#!/usr/local/paper/bin/python
"""
Compute average autocorrelation value (Jy) for a grid of LSTs in all
available data. 
"""

import aipy as a, numpy as n, pylab as p, math as m,sys, optparse, pprint,cPickle,mstat
o = optparse.OptionParser()
a.scripting.add_standard_options(o, pol=True,loc=True,dec=True)
o.add_option('-f','--freq',dest='freq',
             help="""Edge of a desired channel [GHz]""")
o.add_option('--bw',dest='bw',
              help="""Width of channel [kHz]""")
opts, args = o.parse_args(sys.argv[1:])
opts.bw = float(opts.bw)/10**6 #convert to GHz
uv = a.miriad.UV(args[0])
chan = str(str(round((float(opts.freq)-
            float(uv['sfreq']))/float(uv['sdf']))).split('.')[0]+','+
         str(round((float(opts.freq)+float(opts.bw)-
                    float(uv['sfreq']))/float(uv['sdf']))).split('.')[0])
del(uv)

dd = {}
#load the array
for file in args:
    print "loading file :",file,
    uv = a.miriad.UV(file)
    aa = a.loc.get_aa(opts.loc, uv['sdf'], uv['sfreq'], uv['nchan'])
    chans = a.scripting.parse_chans(chan,uv['nchan']) 
    a.scripting.uv_selector(uv,'auto', opts.pol)
    uv.select('decimate',opts.decimate,opts.decphs)
    
    for (uvw,t,(i,j)),d in uv.all():
        d = abs(n.ma.compressed(d.take(chans)).sum()/len(d))
        if d!=n.NaN:
            aa.date = a.ant.juldate2ephem(t)
            if not dd.has_key(i): dd[i] = [[aa.sidereal_time()*12/n.pi,d]]
            #print [aa.sidereal_time(),d.sum()/len(d)]
            else: dd[i] = n.append(dd[i],[[aa.sidereal_time()*12/n.pi,d]],axis=0)
        #print i,dd[i]
        #p.subplot(211)
    print "memory usage [GB]:",mstat.memory()/1024/1024/1024
autofile = open('autos.dat','wb')
cPickle.dump(dd,autofile)
autofile.close()
p.plot(n.vstack(n.array(dd.values()))[:,0],n.vstack(n.array(dd.values()))[:,1],'.',alpha=0.5,markersize=0.1)
times = n.arange(0,24,0.1)
#dda = dict.fromkeys(times[1:-1])
#for k,d in dda.iteritems(): dda[k] = [0,0]
dda = {}
for t in times[1:-1]: dda[t]=[0,0]
#print dda
for cnt,t in enumerate(times):
    if cnt>=1 and cnt<(len(times)-1):
        nsamp=0
        for ant,auto in dd.iteritems():
            for d in auto:
               if d[0]<times[cnt+1] and d[0]>times[cnt-1]:
                   dda[t][0] += d[1]
                   dda[t][1] += d[1]**2
                   nsamp += 1
                # print nsamp
        #if nsamp>0: print t,dda[t],nsamp,dda[t][0]/nsamp
        if nsamp>0: dda[t][:] = [dda[t][0]/nsamp,m.sqrt(n.abs(dda[t][0]**2/nsamp**2 - dda[t][1]/nsamp))];  
#print n.array(dda.values())[:,1]
#print n.max(dd[1][:,1])/n.max(dda.values())
#p.plot(dda.keys(),n.array(dda.values())[:,0],'.r')
p.errorbar(dda.keys(),n.array(dda.values())[:,0],yerr=n.array(dda.values())[:,1],fmt='.r')
#save the lst/auto data in a pickle
afile = open('gal_auto.dat','wb')
cPickle.dump(dda,afile)
afile.close()
fit = n.polyfit(dd[1][:,0],dd[1][:,1],6)
pprint.pprint(fit)
#auto_fit = n.poly1d(fit)
#p.plot(times,auto_fit(times),'-k')
#print FT,len(FT) 
#p.subplot(212)
#p.plot(f,FT)
#print dd
p.show()
