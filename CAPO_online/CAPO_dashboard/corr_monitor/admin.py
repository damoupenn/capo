#
#  admin.py
#  
#
#  Created by Danny Jacobs on 3/15/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#
from CAPO_dashboard.corr_monitor.models import *
from django.contrib import admin
"""
class DBInline(admin.TabularInline):
   model = CorrDB
   extra = 3
class SettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Date information', {'fields': ['pub_date'],'classes':['collapse']}),
    ]
    inlines = [DBInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name','pub_date']
    date_hierachy = 'pub_date'
"""
#admin.site.register(Settings,SettingsAdmin)
admin.site.register(Setting)
admin.site.register(CorrDB)

