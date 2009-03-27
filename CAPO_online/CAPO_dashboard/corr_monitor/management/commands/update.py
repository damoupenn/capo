#!/usr/bin/env python
#
#  update.py
#  
#
#  Created by Danny Jacobs on 3/26/09.
#  Copyright: Creative Commons or something
#
import corr.plotdb
from CAPO_dashboard.corr_monitor.models import CorrDB 
from django.http import HttpResponseRedirect
import sys,os,time
from CAPO_dashboard.corr_monitor.views import update
from django.core.management.base import BaseCommand 

class Command(BaseCommand):
    pass
print sys.argv[2]
db_id = int(sys.argv[2])
#get my own PID and write to the db
db,success = CorrDB.objects.get_or_create(pk=db_id)
db.daemon_id = os.getpid()
db.save()
#loop 
  # update the db, on _any_ kind of error erase the PID and turn off.
while CorrDB.objects.get(pk=db_id).daemon_id:
    try: update([],db_id=db_id)
    except: 
        db.daemon_id=None
        db.save()
        time.sleep(0.5)
        break
