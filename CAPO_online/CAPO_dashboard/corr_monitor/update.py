#!/usr/bin/env python
#
#  update.py
#  
#
#  Created by Danny Jacobs on 3/26/09.
#  Copyright: Creative Commons or something
#
import corr.plotdb
#from models import update 
from django.http import HttpResponseRedirect
import sys,os
from views import update
from models import Log, Visibility, Setting

def scan_log(db):
    """
    Scan the data in the database, save a log entry for each time.
    """
    viss = Visiblity.objects.all()
    corrdb = corr.plotdb.NumpyDB(db.dbfilename)    
    for vis in viss:
        vis.check_vis()
        ws = Warning.objects.all().filter(baseline=vis.pk)
        L  = Log(vis=vis,warnings=ws)
        dataseries = corrdb.read(str(vis.baseline))
        L.save(dataseries)
    



db_id = sys.argv[0]
#get my own PID and write to the db
db = CorrDB.objects.get_or_create(pk=db_id)
db.daemon_id = os.getpid()
db.save()
#loop 
  # update the db, on _any_ kind of error erase the PID and turn off.
update([],db_id=db_id)
while 1:
    try: scan_log(db)
    except: 
        db.daemon_id=None
        db.save()
        break
