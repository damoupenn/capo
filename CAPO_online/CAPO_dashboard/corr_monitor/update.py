#!/usr/bin/env python
#
#  update.py
#  
#
#  Created by Danny Jacobs on 3/26/09.
#  Copyright: Creative Commons or something
#
import corr.plotdb
from models import update 
from django.http import HttpResponseRedirect
import sys,os
from CAPO_dashboard.corr_monitor.views import update
db_id = sys.argv[0]
#get my own PID and write to the db
db = CorrDB.objects.get_or_create(pk=db_id)
db.daemon_id = os.getpid()
db.save()
#loop 
  # update the db, on _any_ kind of error erase the PID and turn off.
while 1:
    try: update([],db_id=db_id)
    except: 
        db.daemon_id=None
        db.save()
        break
