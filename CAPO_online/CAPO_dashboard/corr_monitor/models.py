from django.db import models
from django.contrib import admin
import corr.plotdb
from CAPO_dashboard.corr_monitor.config import *
from CAPO_dashboard.corr_monitor.warning_funcs import *
from numpy import *


class Setting(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=200)
    refdb = models.ForeignKey('CorrDB',related_name="ref_db_id",blank=True,null=True)
    current_db = models.ForeignKey('CorrDB',related_name="cur_db_id",blank=True,null=True)
    bl_gain_silence = models.BooleanField(default=False)
    ant_gain_silence = models.BooleanField(default=False)
    question = models.CharField(max_length=200,blank=True,null=True   )
    pub_date = models.DateTimeField('date last used',auto_now=True)
    bl_amp_upper_threshold = models.FloatField(blank=True,null=True)
    ant_amp_upper_threshold = models.FloatField(blank=True,null=True)
    lat = models.CharField(max_length=20,blank=True,null=True)
    lon = models.CharField(max_length=20)
    filter = models.ForeignKey('Filter',blank=True,null=True)
    modes = (('inspect','inspect'),
        ('stream','stream'))
    mode = models.CharField(max_length=50,choices=modes)
    
class PlotSetting(models.Model):
    def __unicode__(self):
        return str(self.id)   
    ymin = models.FloatField(blank=True,null=True)
    ymax = models.FloatField(blank=True,null=True)
    visibility = models.ForeignKey('Visibility',blank=True,null=True)
    xmin = models.FloatField(blank=True,null=True)
    xmax = models.FloatField(blank=True,null=True)
    xaxis_types = (
       ('freq','freq'),
       ('chan','chan')
    )
    xaxis = models.CharField(max_length=25,choices=xaxis_types,default='freq')
    plot_types = (
       ('plot','linear'),
       ('semilogx','semilogx'),
       ('semilogy','semilogy'),
       ('loglog','loglog')      
    )
    plot_func = models.CharField(max_length=50,choices=plot_types,default='plot')
    data_funcs = (
        ('abs','abs'),
        ('phs','phs')
#        ('abs&phs','abs&phs'),
#        ('complex','complex')
    )
    data_func = models.CharField(max_length=50,choices=data_funcs,default='abs')
admin.site.register(PlotSetting)
class CorrDB(models.Model):
    def __unicode__(self):
        return self.filename
    filename = models.FilePathField(
        path=dbpath,
        match=".*\.db",
        #recursive=True,
        max_length=200)
    daemon_id = models.IntegerField(blank=True,null=True)
    #def copy(self,name):
    #   """ Saves a copy of the DB file TODO"""
    
class Warning_func(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=200)
    function = models.CharField(max_length=50)
    parms=models.CharField(max_length=50)
    active = models.BooleanField(blank=True,null=True)
admin.site.register(Warning_func)    
class Warning(models.Model):
    def __unicode__(self):
        return str(self.type)+str(self.baseline) + str(self.datetime)
    type = models.ForeignKey('Warning_func')
    baseline = models.ForeignKey('Visibility')
    datetime = models.DateTimeField(auto_now_add=True)
admin.site.register(Warning)
class Filter(models.Model):
    def __unicode__(self):
      return self.name
    name = models.CharField(max_length=100)
    pols = (
        ('x','x'),
        ('y','y')
        )
    polA = models.CharField(max_length=1,choices=pols,blank=True,null=True)
    polB = models.CharField(max_length=1,choices=pols,blank=True,null=True)
    antA = models.IntegerField(blank=True,null=True)
    antB = models.IntegerField(blank=True,null=True)
    auto = models.BooleanField(blank=True,null=True)
    cross= models.BooleanField(blank=True,null=True)
    warning = models.ManyToManyField('Warning_func',blank=True,null=True)

admin.site.register(Filter)
class Log(models.Model):
    def __unicode__(self):
        return str(self.vis)+"  |  "+ str(self.datetime)
    vis = models.ForeignKey('Visibility')
    avg = models.FloatField()
    max = models.FloatField()
    min = models.FloatField()
    def save(self,dataseries):
        #WARNING/TODO NB: Injecting noise for testing purposes!!
        dataseries = random.normal(abs(dataseries),0.1)
        ####
        self.avg = average(abs(dataseries))
        self.max = max(abs(dataseries))
        self.min = min(abs(dataseries))
#        self.warnings = Warning.objects.all().filter(baseline=self.vis)
        super(Log, self).save()
    datetime = models.DateTimeField(auto_now_add=True)
    warnings = models.ManyToManyField('Warning_func',blank=True,null=True)
admin.site.register(Log)
class Visibility(models.Model):
    def __unicode__(self):
        return self.antA +' - ' + self.antB
    polerizations = (
    ('xx','xx'),
    ('yy','yy'),
    ('xy','xy'),
    ('yx','yx'),
    )
#    warning = models.ManyToManyField('Warning')
    pol = models.CharField(max_length=2,choices=polerizations)
    score = models.FloatField()
    baseline = models.CharField(max_length=7)
    antA = models.CharField(max_length=4)
    antB = models.CharField(max_length=4)
    is_auto = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Visibilities"
    def check_vis(self):
        """
        Check out a visibility against all activated warning functions.
        """
        aws = Warning_func.objects.exclude(active=False)
        for wfunc in aws:
            exec('wtest = '+wfunc.function+'(self'+',['+wfunc.parms+'])')
            if wtest:
                w,created = Warning.objects.get_or_create(type=wfunc,
                        baseline=self)
                w.save()
            else:
                try: 
                    ws = Warning.objects.all().filter(type=wfunc,baseline=self)
                    for w in ws:w.delete()
                except(Warning.DoesNotExist): pass
        iaws = Warning.objects.all().exclude(type__active__exact=True)
        for wf in iaws: wf.delete()
                
    
                

admin.site.register(Visibility)
