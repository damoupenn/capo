from django.conf.urls.defaults import *
from django.contrib import databrowse
from CAPO_dashboard.corr_monitor.models import Visibility
databrowse.site.register(Visibility)
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^CAPO_dashboard/', include('CAPO_dashboard.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^databrowse/(.*)',databrowse.site.root),
    #(r'^corr/',include('CAPO_dashboard.corr.urls')),
    (r'^corr_monitor/$','CAPO_dashboard.corr_monitor.views.index'),
    (r'^corr_monitor/vis/(?P<vis_id>\d+)/$','CAPO_dashboard.corr_monitor.views.vis_detail'),
    (r'^corr_monitor/update/$','CAPO_dashboard.corr_monitor.views.update'),
    (r'^corr_monitor/settings/$','CAPO_dashboard.corr_monitor.views.update_settings'),
    (r'^corr_monitor/filters/$','CAPO_dashboard.corr_monitor.views.filters'),
    (r'^corr_monitor/filters/(?P<f_id>\d+)/$','CAPO_dashboard.corr_monitor.views.filter_detail'),
    (r'^corr_monitor/filters/(?P<f_id>\d+)/toggle/$','CAPO_dashboard.corr_monitor.views.filter_toggle'),
    (r'^corr_monitor/filters/(?P<f_id>\d+)/update/$','CAPO_dashboard.corr_monitor.views.filter_detail'),
    (r'^corr_monitor/filters/save/$','CAPO_dashboard.corr_monitor.views.filter_detail'),
    (r'^corr_monitor/filters/add/$','CAPO_dashboard.corr_monitor.views.filter_detail') #TODO: Possibly rename select to filters/modify.html?
    #(r'^corr_monitor/corr.css',include('CAPO_dashboard.corr_monitor.corr.css'))
)
urlpatterns += patterns('', (r'^corr_monitor/media/(.*)', 'django.views.static.serve', {'document_root':'/Users/danny/Work/radio_astronomy/Software/CAPO/CAPO_online/CAPO_dashboard/templates/corr_monitor/media/', 'show_indexes': True}), )