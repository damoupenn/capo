#!/usr/global/paper/bin/python

#scores two UV waterfall plots

import aipy as a, ephem as e, numpy as np, sys, optparse, os, pylab as p, time, qPickle

starttime = time.time()

o = optparse.OptionParser()
o.set_usage('score_uv.py data.uv [options]')
o.set_description(__doc__)
a.scripting.add_standard_options(o, pol=True, cmap=True, cal=True,
    src=True)
o.add_option('--maxiter', dest='maxiter', type='int', default=1,
    help='Maximum number of iterations in MCMC')
o.add_option('--clean', dest='clean', type='float',
    help='Deconvolve delay-domain data by the "beam response" that results from flagged data.  Specify a tolerance for termination (usually 1e-2 or 1e-3).')

opts,args = o.parse_args(sys.argv[1:])
cmap=p.get_cmap(opts.cmap)

#global parameters
sigma_peak = 1 #pixels
sigma_noise = 100. #Jy/channel

#read in data and initialize antenna array
uv = a.miriad.UV(args[0])
aa = a.cal.get_aa(opts.cal, uv['sdf'], uv['sfreq'], uv['nchan'])
srclist,cutoff,catalogs = a.scripting.parse_srcs(opts.src, opts.cat)
cat = a.cal.get_catalog(opts.cal, srclist, cutoff, catalogs)

#nbls = a.scripting.parse_ants('cross', data['nants'])
#print nbls
#if len(nbls) != data['nants']: raise ValueError("select only one antenna!")
#bl_zero = nbls[0][0]
#ant_zero = a.miriad.bl2ij(bl_zero)
#ant_zero_str = str(ant_zero[0])+'_'+str(ant_zero[0])
#ant_zero_str = '0_0'
#a.scripting.uv_selector(uv, ant_zero_str, opts.pol)

#create model visibilities peaked at center of DDR space
print "creating peak model"
shape_out=[]
ants = {}
for (uvw, t, (i,j)), dshape in uv.all():
    if i == j == 0: shape_out.append(dshape)
    ant = str(i)
    if not ants.has_key(i): ants[i] = []
del(uv)# -- keep this at one baseline sized waterfall plot
shape_out = np.array(shape_out)
y = np.arange(shape_out.shape[0])
x = np.arange(shape_out.shape[1])
filter = np.zeros(shape_out.shape)
del(shape_out)

"""
#gaussian
for i in x:
    for j in y:
        filter[j, i] = np.exp(-1 * ((i - x[-1]/2.)/sigma_peak)**2) * np.exp(-1 * ((j - y[-1]/2.)/sigma_peak)**2)
"""
#lorentzian
for i in x:
    for j in y:
        filter[j, i] = (sigma_peak/((i - x[-1]/2.)**2 + sigma_peak**2)) * (sigma_peak/((j - y[-1]/2.)**2 + sigma_peak**2))

#clean RFI gaps in the data
def clean(uv, p, d):
    uv.select('auto', -1, -1, include=False)
    mask = d.mask
    #delay transform and clean
    dflags = np.logical_not(d.mask).astype(np.float)
    dgain = np.sqrt(np.average(dflags**2))
    dker = np.fft.ifft(dflags)
    d = d.filled(0)
    d = np.fft.ifft(d)
    if not opts.clean is None and not np.all(d == 0):
        d, info = a.deconv.clean(d, dker, tol=opts.clean)
	d += info['res'] / dgain
    d = np.ma.array(d)
    d = np.ma.concatenate([d[d.shape[0]/2:],
			   d[:d.shape[0]/2]], axis=0)
    #inverse delay tranform
    d = np.fft.fft(d)
    d = np.ma.array(d)
    d.mask = np.zeros_like(mask)
    return p, d
    
#the scoring
def score_sim(file, aa, prms, iter, oldscore):
    total_score = 0.
    if iter == 1:
        tprms = aa.get_params(prms)
        oldprms = tprms
        cat.set_params(tprms)
    else:
        tprms = aa.get_params(prms)
	oldprms = tprms
        for antkey in tprms.keys():
	    for coordkey in tprms[antkey].keys():
	        #print tprms[antkey][coordkey]
	        tprms[antkey][coordkey] += float(np.random.normal(0., 3.3, 1))
	aa.set_params(tprms)
	cat.set_params(tprms)
    print "Iteration %d" % iter
    iter += 1
    data = a.miriad.UV(file)
    #data.select('antennae', int(ant), -1)
    data.select('auto', -1, -1, include=False)
    #loop over sources
    for k in cat:
        print "    source:", k
	dout = {}
	data.rewind()
	for (uvw, t, (i, j)), d in data.all():
        #reset the positions of antennas in the antenna array

            #distinguish between baselines
	    bl = '%d,%d' % (i,j)
            #phase data to source
            aa.set_jultime(t)
	    cat.compute(aa)
	    d = d * aa.gen_phs(cat[k], i, j)
            d.shape = (1,) + d.shape
	    if not dout.has_key(bl): dout[bl] = []
	    dout[bl].append(d)
            
	bls = dout.keys()
        for cnt, bl in enumerate(bls):
            #print np.array(dout[bl]).shape
            if cnt == 0: dsum = np.zeros(np.array(dout[bl]).shape)
            dsum = dsum + dout[bl]
        #delay transform d (no cleaning)
        d = np.ma.array(dsum).filled(0)
        d = np.fft.ifft(d)
        d = np.ma.array(d)
        d = np.ma.concatenate([d[d.shape[0]/2:],
					       d[:d.shape[0]/2]], axis=0)


        #delay rate transform
        
        d = np.fft.ifft(d, axis=0)
	    #if not opts.clean is None:
	    #    for chan in range(d.shape[1]):
	    #        d[:,chan],info = a.deconv.clean(d[:,chan],dker,
	    #						tol=opts.clean)
	    #	    d[:,chan] += info['res'] / dgain
        d = np.ma.concatenate([d[d.shape[0]/2:],
					       d[:d.shape[0]/2]], axis=0)

            #ready d for plotting
        d = np.ma.absolute(d.filled(0))
        d = np.ma.masked_less_equal(d, 0)
	    #d = np.ma.log10(d)
    
            #calculate the score: correlation w/ peak for each source
        cor_score = np.ma.sum((-1*filter)*d)
        total_score = cor_score + total_score


    del(data)
    #multiply by the prior score
    prior_score = 1.
    total_score = total_score * prior_score

    if iter == 2: #added 1 previously
        oldscore = total_score
    else:
        rand = np.random.uniform(0., 1., 1)
        print rand
        print total_score/oldscore
        if rand > (total_score/oldscore):
            print 'step rejected'
            tprms = oldprms
            aa.set_params(tprms)
            cat.set_params(tprms)
            total_score = oldscore

    #plot
    #p.subplot(2,1,1)
    #p.imshow(d,aspect='auto',cmap=cmap)#, vmin=-8, vmax=8)
    #p.colorbar()
    #p.subplot(2,1,2)
    #p.imshow(filter,aspect='auto',cmap=cmap)#, vmin=-8, vmax=8)
    #p.colorbar()
    #p.show()

    return total_score, iter, tprms

for filename in args:
    print 'Reading', filename
    print 'cleaning data'
    uvi = a.miriad.UV(filename)
    uvo = a.miriad.UV(filename+'.clean', status='new')
    uvo.init_from_uv(uvi)
    uvo.pipe(uvi, mfunc=clean)
    del(uvo)

    iter = 1.
    prms = {}
    results = {}
    for it in range(opts.maxiter):
        if iter == 1:
            oldscore = 1.
	    for ant in ants.keys():
	        pd = a.scripting.parse_prms(str(ant)+'=(x/y/z)')
		prms.update(pd)
	    score, iter, nprms = score_sim(filename, aa, prms, iter, oldscore)
            oldscore = score
	    print 'score == ', score
	    results[str(iter-1)] = nprms
            scr = {'score' : score}
	    results[str(iter-1)].update(scr)
	else:
	    score, iter, nprms = score_sim(filename, aa, prms, iter, oldscore)
            oldscore = score
	    print 'score ==', score
	    results[str(iter-1)] = nprms
            scr = {'score': score}
	    results[str(iter-1)].update(scr)
    
    command = "rm -r %(file)s" % {"file" : filename+".clean"}
    os.system(command)
    endttime = time.time()
    print "Run time", endttime-starttime
    qPickle.save(results, 'scores.pkl',clobber=True)
    
