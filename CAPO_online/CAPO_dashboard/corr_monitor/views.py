# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from CAPO_dashboard.corr_monitor.models import * 
from django.template import Context, loader
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseNotFound
from django.core.urlresolvers import reverse
import math as m,numpy as np,os
from django.contrib import admin
import corr.plotdb
from django.forms import ModelForm
import pylab as pl,types
from CAPO_dashboard.corr_monitor.config import *
import CAPO_dashboard.corr_monitor.warning_funcs as warning_func_set
from CAPO_dashboard.corr_monitor.warning_funcs import *
from matplotlib import font_manager
import datetime
dbfilename = '/Users/danny/Work/radio_astronomy/Software/CAPO/CAPO_online/CAPO_dashboard/corr_monitor/corr.db'
vistablewidth = 500
rewire = {
   6: {'x': 8, 'y': 9},
   7: {'x':10, 'y':11},
   4: {'x': 4, 'y': 5},
   5: {'x': 6, 'y': 7},
   2: {'x': 0, 'y': 1},
   3: {'x': 2, 'y': 3},
   0: {'x':12, 'y':13},
   1: {'x':14, 'y':15},
}
class CorrDBForm(ModelForm):
    """
    Defines a form used to start/stop logging daemon.
    """
    class Meta:
        model=CorrDB
class Warning_funcForm(ModelForm):
    """
    Defines a form used to set un-common settings.
    """
    class Meta:
        model = Warning_func
class SettingsForm(ModelForm):
    """
    Defines a form used to set un-common settings.
    """
    class Meta:
        model = Setting
class DBForm(ModelForm):
    """
    Defines a form used to set the current data database
    """
    class Meta:
        model = Setting
        fields = ('refdb','mode',)
class FilterForm(ModelForm):
    """
    Defines a form used to apply data filtering etc settings to dashboard
    """
    class Meta:
        model = Filter
class PlotSettingForm(ModelForm):
    """
    Defines a form used to set plotting variables
    """
    class Meta:
        model = PlotSetting
        exclude = ('visibility',)
#def select(request):
#    """
#    Create a new filter.
#    """
#    if request.method == 'POST':  #if data is submitted, process it.
#        form = FilterForm(request.POST)
#        if form.is_valid():
#            return HttpResponse(str(form.cleaned_data['id']))
##            form.save()       
##            return HttpResponseRedirect('/corr_monitor/filters/')
#    else: 
#        form = FilterForm()
#    return render_to_response('corr_monitor/select.html', {
#        'form':form,
#        })
def filter_detail(request,f_id=0):
    """
    Edit an existing Filter or create a new one.
    """
    if f_id==0:
        if request.method=='POST':
            form = FilterForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/corr_monitor/filters/')
        else:
            form = FilterForm()
            action = '/corr_monitor/filters/save/'
    
    else:
        try: filter = Filter.objects.get(id=f_id)
        except(Filter.DoesNotExist): 
            return HttpResponseRedirect('/corr_monitor/filters/add/')
        if request.method=='POST':
            form = FilterForm(request.POST,instance=filter)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/corr_monitor/filters/')
        else:
            form = FilterForm(instance=filter)
            action = '/corr_monitor/filters/'+str(f_id)+'/update/'
    return render_to_response('corr_monitor/filter_detail.html', {
        'form':form,
        'action':action
        })
def warning_funcs_detail(request,wf_id=0):
    """
    Display a list of available warning functions. Indicate which ones are applied.
    """
    s = load_settings()
    if wf_id==0:
        if request.method=='POST':
            form=Warning_funcForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/corr_monitor/filters/')
        else:
            form = Warning_funcForm()
            action = '/corr_monitor/warning_funcs/save/'
    else:
        try: warning_func = Warning_func.objects.get(id=wf_id)
        except(Warning_func.DoesNotExist):
            return HttpResponseRedirect('/corr_monitor/warning_funcs/save/')
        if request.method=='POST':
            form = Warning_funcForm(request.POST,instance=warning_func)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/corr_monitor/warning_funcs/')
        else:
            form = Warning_funcForm(instance=warning_func)
            action = '/corr_monitor/warning_funcs/'+str(wf_id)+'/update/'
    h = ['<h3>Help</h3>']
    for a in dir(warning_func_set):
        if isinstance(getattr(warning_func_set, a, None),types.FunctionType):
            h.append('<b>'+a+':</b>')
            exec('h.append('+a+'.__doc__)')
    return render_to_response('corr_monitor/form_detail.html',{
        'form':form,
        'action':action,
        'help':h        
        })
def warning_func_toggle(request,wf_id=0):
    """
    Toggle a warning on or off.
    """
    try: warning_func = Warning_func.objects.get(id=wf_id)
    except(Warning_func.DoesNotExist):
        return HttpResponseRedirect('/corr_monitor/warning_funcs/save/')
    warning_func.active = not(warning_func.active)
    warning_func.save()
    return HttpResponseRedirect('/corr_monitor/warning_funcs/')

def warning_funcs(request):        
    warning_funcs = Warning_func.objects.all()
    return render_to_response('corr_monitor/warning_funcs.html',{
        'warning_funcs':warning_funcs
        })
def filters(request):
    """
    Displays a list of available filters. And some other stuff that I always
    want to be showing.
    """
    settings  = load_settings()
    #current_filter = Filter.objects.filter(id=settings.filter_id)
    filters = Filter.objects.exclude(id=settings.filter_id)
    return render_to_response('corr_monitor/filters.html', {
        'filters':filters,
        'current_filter':settings.filter
       })
       
def load_settings():
    setting,created = Setting.objects.get_or_create(lon='45',name='Default')
    return setting
def update_settings(request):
    s = load_settings()
    if request.method=='POST':
        form = DBForm(request.POST,instance=s)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/corr_monitor/')
    else:
        form = SettingsForm(instance=s)
    return render_to_response('corr_monitor/setting_detail.html',
       {'form':form})
    
def help(request):
    return render_to_response('corr_monitor/help.html')
        
def filter_toggle(request,f_id):
    """
    Toggles a filter in current settings.
    """
    #load setting
    setting = load_settings()
    if setting.filter_id==f_id:
        setting.filter_id=0
    else:
        setting.filter_id = f_id
    setting.save()
    return HttpResponseRedirect('/corr_monitor/filters/')  
             
def key2bl(old_key):
    """
    Re-do a dbm to match physical wiring. (eg correct_ script)
    """
    ants,pol = old_key.split(',')
    polA,polB = pol[0],pol[1]
    antA,antB = ants.split('-')
    if antA==antB and pol=='yx': return "","",True
    antA = str(rewire[int(antA)][polA])
    antB = str(rewire[int(antB)][polB])
    polA = polB = 'y'
    return antA+polA,antB+polB,False

def toggle_update_daemon(request,db_id):
    """
    Starts or stops daemon that updates database with db_id.
    """
    HttpResponseRedirect('/corr_monitor/')
    
    
def update(request,db_id=0):
    """
    Loads all visibility records from given filename.
    """
    #filename=dbfilename
    s = load_settings()
    if db_id==0: filename = s.refdb.filename
    else: filename = CorrDB.objects.get(pk=db_id).filename
    db = corr.plotdb.PlotDB(filename)
    keys = db.keys()
    keys.sort()
    html = ""
    for k in keys: 
        #find the auto-correlations:
        try: indx=k.index('-')
        except: continue
        #print 'Found - at index %i in key %s'%(indx,k)
        #print 'Comparing %s to %s.'%(k[0:indx],k[indx+1:-3])
        antA,antB,skip = key2bl(k)
        if skip:continue
        if (antA==antB): is_auto=1
        else: is_auto=0
        #No warnings are generated until the score has been computed.
#        warning = Warning.objects.get(name="None")
        #chech for existing baselines
        try: 
            old_v = Visibility.objects.filter(antA=antA).get(antB=antB)
            oldid = old_v.id
        except(Visibility.DoesNotExist):oldid = None
        new_v = Visibility(
            baseline=k,
            antA = antA,
            antB = antB,
            is_auto=is_auto,
            score=0,   
            id=oldid)
        new_v.save()
#        new_v.warning.add(warning)
#        new_v.save()
        #print Visibility.objects.all()
        #html = html +"."+ bl
    return HttpResponseRedirect('/corr_monitor/')
    #return HttpResponse(html)   
   
def get_vis(f=None):
    """
    Queries the visibility table applying filter in QuerySet f.
    TODO: support warnings.
    """

    v_string = "v = Visibility.objects.all()"
    
    if not f is None:            
        for k,d in f.values()[0].iteritems():
            if not d is None:
                if k is 'auto' and d:
                    v_string = v_string + ".extra(where=['antA=antB'])"
                if k is 'cross' and d:
                    v_string = v_string + ".extra(where=['antA<>antB'])"
                if k is 'antA':
                    v_string = v_string + ".filter(antA__regex=r'"+"^"+str(d)+"[a-z]"+"')"
                if k is 'antB':
                    v_string = v_string + ".filter(antB__regex=r'"+"^"+str(d)+"[a-z]"+"')"
                if k is 'polA':
                    v_string = v_string + ".filter(antA__contains='"+str(d)+"')"
                if k is 'polB':
                    v_string = v_string + ".filter(antB__contains='"+str(d)+"')"
        if len(f[0].warning.all())>0:
            wname = str(f[0].warning.all()[0])
            v_string = v_string + ".filter(warning__type__name__exact='"+str(wname)+"')"

#    print Visibility.objects.all().filter(warning__type__name__exact='Low level')
    print v_string
    exec(v_string)
    return v
 
def index(request):
    s = load_settings()
    filter = Filter.objects.all().filter(id=s.filter_id)
    v = get_vis(f=filter)
    dbform = DBForm(instance=s)
#    cdbform = CorrDBForm(instance=s.refdb)
    if len(v)==0:
            return render_to_response('corr_monitor/main.html',
    {'settings': s,
      'dbform':dbform})
    db = corr.plotdb.NumpyDB(s.refdb.filename)
    if v.count()>0:
        m2 = int(m.sqrt(float(v.count())))
        m1 = int(m.ceil(float(v.count()) / m2))
    else:
        m2 = 1
        m1 = 1
    tdwidth = str(vistablewidth/m1)+'px'
    n=0
    table = ""
    v.order_by('antA')#.order_by('antB')
    for i in range(m2):
        table =table + "<tr>"
        for j in range(m1):           
           if n<v.count():
              v[n].check_vis()
              dataseries = db.read(str(v[n].baseline))            
              #NB: We only show the top-most warning. Order is arbitrary.
              ws = Warning.objects.all().filter(baseline=v[n].pk)
              if len(ws)==0: classname = 'None'
              else: classname = str(ws[0].type)
              table = table + "<td class=\""+ classname +"\""
              table = table + " onmouseover= \"this.className="
              table = table + "'"+ classname +  " mouseborder'\" "
              table = table + " onmouseout = \"this.className='"+classname+"'\""
              table = table + "style=\"width:"+tdwidth
              table = table + "; height:"+tdwidth + "\" >"
              table = table + "<span style=\"font-size:10pt\">"
              table = table + "<a href=\"vis/"+str(v[n].id)+"\"/>"
              table = table + str(v[n].antA)
              table = table + "<br> "+str(v[n].antB)
              table = table + "</span></a>"
              table = table + "<br>"
              table = table + str(round(np.average(np.abs(dataseries)),2))
#              table = table + str(v[n].score)
              table = table + "</td>"
              n +=1
        table = table + "</tr>"
    v.rows = table
    #select all baselines with warnings.name!=None
    w = Warning.objects.all()
    return render_to_response('corr_monitor/main.html',
    {'settings': s,'visibilities':v,'warnings':w,
      'dbform':dbform,'time':v[0].datetime})
def trace(request):
    """
    Plot a historical trace for all baselines selected by the current filter.
    TODO draw warning thresholds.
    """
    #Load settings, filters etc
    s = load_settings()
    filter = Filter.objects.all().filter(id=s.filter_id)
    v = get_vis(f=filter)
    db = corr.plotdb.NumpyDB(s.refdb.filename)
    w = Warning.objects.all()
    dbform = DBForm(instance=s)
    outfile = '/corr_monitor/media/img/trace'+str(os.getpid())+'.png'
    fig = pl.figure()
    
    #Load plot settings from 
    pset,create = PlotSetting.objects.get_or_create(plot_func='plot_date')
    if request.method=='POST':
#        settingform = PlotSettingForm(request.POST,instance=pset)
#        if settingform.is_valid():
#            settingform.save()
        exec('trange='+str(request.POST['trange']))
        trange = datetime.timedelta(trange)
        HttpResponseRedirect('/corr_monitor/trace/')
    else:
        trange=datetime.timedelta(0)

    #Get data from log
    lines = []
    labels = []
    for vis in v:
        #get the trace vector
        ts = Log.objects.filter(vis=vis)
        avg = []
        time = []
        for t in ts: 
            time.append(t.datetime)
            avg.append(t.avg)
        lines.append(pl.plot(time,avg,label=str(vis),alpha=0.5))
        labels.append(str(vis))
        #print ts
    if trange:
        tmax = n.max(time)
        tmin = tmax-trange
        pset.tmin = tmin
        pset.save()
    else:
      tmin = pset.tmin
      trange = n.max(time)-tmin
    #build plot
    print trange.days*24.0
    pl.title('time range :'+str(round(trange.days*24.0+trange.seconds/(60.0*60)))+' hours or '+
        str(trange.days+round(trange.seconds/(60.0*60*24),3))+' days')
 #   adjust_plot(pset=pset)
    pl.xlim(xmin=tmin)
    fig.autofmt_xdate()
    pl.figlegend(lines,labels,'upper right',prop=font_manager.FontProperties(
    size=7))
    pl.savefig(temproot+outfile,format='png')
    settingform=PlotSettingForm(instance=pset)
    return render_to_response('corr_monitor/main.html',
    {'settings': s,'trace':outfile,'warnings':w,
      'dbform':dbform,'time':v[0].datetime,'plotsetting_form':settingform})    
    
def adjust_plot(vis=None,pset=None):
    """
    Modifies a figure plotting a single visibility. 
    Returns a PlotSetting object.
    Input plotsetting model or visibility model. Visibility will override.
    """
    #get the plot setting corresponding to this guy
    if not vis is None: pset,created =  vis.plotsetting_set.get_or_create(visibility=vis.id)
    if not pset.ymax is None: 
        pl.ylim(ymax=float(pset.ymax))
    if not pset.ymin is None:
        pl.ylim(ymin=float(pset.ymin))
    if not pset.xmin is None:
        pl.xlim(xmin=float(pset.xmin))
    if not pset.xmax is None:
        pl.xlim(xmax=float(pset.xmax))
    if not pset.tmin is None:
        pl.xlim(xmin=float(pset.tmin))
    if not pset.tmax is None:
        pl.xlim(xmax=float(pset.tmax))
    
        #pl.title(str(pset.ymax))

    #... more settings
    return pset
                
def vis_detail(request, vis_id):
    """
    Look at a baseline in detail.
    """
    vis = get_object_or_404(Visibility,pk=vis_id)
    s = load_settings()
    pl.figure()
    pset = adjust_plot(vis)
    messages = []
    if request.method=='POST':
        settingform = PlotSettingForm(request.POST,instance=pset)
        if settingform.is_valid():
            settingform.save()
            messages.append("Graph updated")
            return HttpResponseRedirect('/corr_monitor/vis/'+vis_id+'/')
    db = corr.plotdb.NumpyDB(s.refdb.filename)
    dataseries = db.read(str(vis.baseline))
    outfile = '/corr_monitor/media/img/temp'+str(os.getpid())+'.png'
    if pset.xaxis=='freq':
        fmin = 100
        fmax = 200
        x = np.linspace(fmin,fmax,num=len(dataseries))
    else:
        x = range(len(dataseries))
    if pset.data_func=='abs':
        data = np.abs(dataseries)
    elif pset.data_func=='phs':
        data = np.angle(dataseries)
    else:
        data = dataseries
    exec('pl.'+pset.plot_func+'(x,data)')
#    pl.plot(x,np.abs(dataseries))
    pl.grid()
    pl.ylabel('raw amplitude [V]')
    pset = adjust_plot(vis)
    pl.savefig(temproot+outfile,format='png')
    settingform=PlotSettingForm(instance=pset)
    dbform = DBForm(instance=s)        
    return render_to_response('corr_monitor/vis_detail.html',
         {'vis' : vis,
         'graphs':(outfile,),
         'plotsetting_form':settingform,
         'dbform':dbform,
         'messages':messages
         })
def plot_vs(vis):
    """
    Generate a single plot from a visibility object and return the name of the file.
    """
    s = load_settings()
    pset,created =  vis.plotsetting_set.get_or_create(visibility=-1)
    db = corr.plotdb.NumpyDB(s.refdb.filename)
    dataseries = db.read(str(vis.baseline))
    img_root = '/corr_monitor/media/img/'
    outfile = img_root+str(vis.baseline)+'.png'
    if pset.xaxis=='freq':
        fmin = 100
        fmax = 200
        x = np.linspace(fmin,fmax,num=len(dataseries))
    else:
        x = np.range(len(dataseries))
    if pset.data_func=='abs':
        data = np.abs(dataseries)
    elif pset.data_func=='phs':
        data = np.angle(dataseries)
    else:
        data = dataseries
    exec('pl.'+pset.plot_func+'(x,data)')
#    pl.plot(x,np.abs(dataseries))
    pl.grid()
    pl.ylabel('raw amplitude [V]')
    pset = adjust_plot(vis)
    pl.savefig(temproot+outfile,format='png')
    return outfile

    
def real_time(request):
    """
    Push monitor of baseline averages
    """
    s = load_settings()
    filter = Filter.objects.all().filter(id=s.filter_id)
    v = get_vis(f=filter)
    

