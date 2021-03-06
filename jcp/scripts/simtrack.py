#! /usr/bin/env python
import aipy as a, numpy as n, pylab as p, optparse, sys
import _beamuv as beamuv

o = optparse.OptionParser()
o.set_usage('srcpredict.py -C [calfile] npzfile')
o.add_option('-b','--beam',dest='beam',default='/data3/paper/pober/pgb/pgb16/pgb015/beam04.smoothe.npz',
    help='The beam npz file to use.')
o.add_option('-n','--noise',dest='noise',default=0,
    help='The standard dev. of the noise to add.')
o.add_option('--sim',dest='sim',action='store_true',
    help='Use simulated sources in the pgb015_v008 cal file.')
a.scripting.add_standard_options(o, cal=True,pol=True,src=True)

opts,args = o.parse_args(sys.argv[1:])

_coeffs = beamuv.coeffs_from_file(opts.beam)

srcs = ''
if not opts.sim:
    for src in args:
        srcs +=src.split('__')[0]+','
else:
    srcs = 'aaaaa,aaaa,aaa,aa,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w'
    args = ['aaaaa','aaaa','aaa','aa','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w']
    #srcs = 'aaa'
    #args = ['aaa']
beam = beamuv.BeamUV(_coeffs,.150,size=1000,pol=opts.pol)
#beam._show_()
#p.show()
#sys.exit()
aa = a.cal.get_aa(opts.cal, n.array([.150]))
srclist, cutoff, catalogs = a.scripting.parse_srcs(srcs, opts.cat)
cat = a.cal.get_catalog(opts.cal,srclist)
cat.compute(aa)

#Produce a sourcetrack
for f in args:
    if not opts.sim:
        k = f.split('__')[0]
        npz = n.load(f)
        times = npz['times']
    else:
        times = 2455016. + n.arange(0,1,1.e-3)
        k = f
    print k
    alt, az = [],[]
    for i,t in enumerate(times):
        aa.set_jultime(t)
        cat[k].compute(aa)
        alt.append(cat[k].alt)
        az.append(cat[k].az)
    alt = n.array(alt)
    az = n.array(az)
    x,y,z = a.coord.azalt2top((az, alt))
    #print k,cat[k].jys

    track,mask = [],[]
    for ix,iy,iz in zip(x,y,z):
        if iz > 0:
            track.append((beam.response(n.array([ix]),n.array([iy]),n.array([iz]))**2)*cat[k].jys)
            mask.append(0)
        else:
            mask.append(1)
    if not opts.sim:
        afreqs = npz['afreqs']
        outfile = f.replace('f.npz','s%dcN.npz' % int(opts.noise))
    else:
        afreqs = (n.arange(100.,200,(100./1024)))/1000.
        #print afreqs
        outfile = k+'__s%dcN.npz' % int(opts.noise)
    if opts.noise != 0.:
        print 'adding noise'
        track = n.array(track)
        scale = float(opts.noise)
        noise = n.random.normal(loc=0.,scale=scale,size=track.shape)
        #smooth_noise = n.ones_like(noise)
        #for ind,val in enumerate(noise):
            #smooth_noise[ind] = n.mean(noise[ind-50:ind+50])
            #print noise[ind], smooth_noise[ind]
        track += noise
        track = n.abs(track)
    ones = n.ones_like(afreqs)
    spec = n.outer(track,ones)
    times = n.ma.array(times,mask=mask)
    times = times.compressed()
    n.savez(outfile, times=times, afreqs=afreqs,spec=spec)
