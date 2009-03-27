from django.conf.urls.defaults import *
from CAPO_dashboard.corr.models import Settings
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()
info_dict = {
    'queryset' : Settings.objects.all(),
}
urlpatterns = patterns('',
    (r'^$','django.views.generic.list_detail.object_list',info_dict),
)
