#!/usr/bin/env python
#
#  update.py
#  
#
#  Created by Danny Jacobs on 3/26/09.
#  Copyright: Creative Commons or something
#
import corr.plotdb
from CAPO_dashboard.corr_monitor.models import CorrDB,Log,Visibility,Setting,Warning 
from django.http import HttpResponseRedirect
import sys,os,time
from CAPO_dashboard.corr_monitor.views import update
from django.core.management.base import BaseCommand 
import traceback


class Command(BaseCommand):
    pass
    
def scan_log(db):
    """
    Scan the data in the database, save a log entry for each time.
    """
    viss = Visibility.objects.all()
    corrdb = corr.plotdb.NumpyDB(db.filename)    
    for vis in viss:
        vis.check_vis()
#        ws = Warning.objects.all().filter(baseline=vis.pk)
        L  = Log(vis=vis)
        dataseries = corrdb.read(str(vis.baseline))
        L.save(dataseries)
#        for w in ws: L.warnings.add(w)
#        L.save(dataseries)
    
def main(*argv):
    db_id = int(argv[1])
        #get my own PID and write to the db
    db = CorrDB.objects.get(pk=db_id)
    print "Using database file:"+db.filename
    if db.daemon_id: raise Exception, "Daemon "+str(db.daemon_id)+" is already watching this database."
    db.daemon_id = os.getpid()
    db.save()
    #loop 
      # update the db, on _any_ kind of error erase the PID and turn off.
    print "updating reference database:",
    update([],db_id=db_id)
    print "[Success]"
    while CorrDB.objects.get(pk=db_id).daemon_id:

        try: 
            print ".",
            sys.stdout.flush()
            time.sleep(10)
            scan_log(db)
        except: 
            print traceback.print_exc()
            print "Error during scan. Exiting..."
            db.daemon_id=None
            db.save()
            sys.exit()


if __name__ == 'CAPO_dashboard.corr_monitor.management.commands.update':
    main(*sys.argv[1:])
