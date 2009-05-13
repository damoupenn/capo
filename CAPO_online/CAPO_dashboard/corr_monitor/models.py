from django.db import models
from django.contrib import admin
import corr.plotdb
from config import *

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
class PlotSetting(models.Model):
    def __unicode__(self):
        return str(self.id)   
    ymin = models.FloatField(blank=True,null=True)
    ymax = models.FloatField(blank=True,null=True)
    visibility = models.ManyToManyField('Visibility')
    xmin = models.FloatField(blank=True,null=True)
    xmax = models.FloatField(blank=True,null=True)
    x_zero = models.FloatField(blank=True,null=True)
    x_scale = models.FloatField(blank=True,null=True)
    plot_func = models.CharField(max_length=50,blank=True,null=True)
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
    
class Warning(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=200)
    amp_upper_threshold_ex = models.BooleanField(default=False)
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
    warning = models.ManyToManyField('Warning',blank=True,null=True)

admin.site.register(Filter)
class Visibility(models.Model):
    def __unicode__(self):
        return self.baseline +' - ' + self.pol
    polerizations = (
    ('xx','xx'),
    ('yy','yy'),
    ('xy','xy'),
    ('yx','yx'),
    )
    warning = models.ManyToManyField('Warning')
    pol = models.CharField(max_length=2,choices=polerizations)
    score = models.FloatField()
    baseline = models.CharField(max_length=7)
    antA = models.CharField(max_length=4)
    antB = models.CharField(max_length=4)
    is_auto = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Visibilities"
    
                

admin.site.register(Visibility)
