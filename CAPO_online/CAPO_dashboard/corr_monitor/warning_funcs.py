#
#  warnings.py
#  
#
#  Created by Danny Jacobs on 5/14/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#
import numpy as n
import corr.plotdb

"""
Functions defined here may be applied as a warning trigger in oCAPO.
Call function exactly as named when creating warning.
All warnings are logic positive. Returns True if warning is triggered.
"""

def avg_gain_low_warning(vis,parms):
    """
    Triggers warning if gain is set too low.
    Input a visibility model object and parm list.
    parms = [auto_threshold,cross_threshold]
    Return a boolean True if warning is triggered.
    """
    from CAPO_dashboard.corr_monitor.models import Setting
    s,created = Setting.objects.get_or_create(lon='45',name='Default')
    db = corr.plotdb.NumpyDB(s.refdb.filename)
    dataseries = db.read(str(vis.baseline))
    auto_threshold = parms[0]
    cross_threshold = parms[1]
    if vis.antA==vis.antB:
        if n.average(n.abs(dataseries))<auto_threshold: return True
    else:
        if n.average(n.abs(dataseries))<cross_threshold: return True
    return False