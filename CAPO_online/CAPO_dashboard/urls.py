from django.conf.urls.defaults import *
from django.contrib import databrowse
from CAPO_dashboard.corr_monitor.models import Visibility

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from CAPO_dashboard.corr_monitor.config import *
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
    (r'^corr_monitor/help/$','CAPO_dashboard.corr_monitor.views.help'),
    (r'^corr_monitor/filters/add/$','CAPO_dashboard.corr_monitor.views.filter_detail'), 
    (r'^corr_monitor/warning_funcs/$','CAPO_dashboard.corr_monitor.views.warning_funcs'),
    (r'^corr_monitor/warning_funcs/(?P<wf_id>\d+)/$','CAPO_dashboard.corr_monitor.views.warning_funcs_detail'),
    (r'^corr_monitor/warning_funcs/(?P<wf_id>\d+)/toggle/$','CAPO_dashboard.corr_monitor.views.warning_func_toggle'),
    (r'^corr_monitor/warning_funcs/(?P<wf_id>\d+)/update/$','CAPO_dashboard.corr_monitor.views.warning_funcs_detail'),
    (r'^corr_monitor/warning_funcs/new/$','CAPO_dashboard.corr_monitor.views.warning_funcs_detail'),
    (r'^corr_monitor/trace/$','CAPO_dashboard.corr_monitor.views.trace'),
    #(r'^corr_monitor/corr.css',include('CAPO_dashboard.corr_monitor.corr.css'))
)
urlpatterns += patterns('', (r'^corr_monitor/media/(.*)', 'django.views.static.serve', {'document_root':document_root, 'show_indexes': True}), )