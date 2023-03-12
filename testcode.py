# import sys
# C:\Users\hanne\OneDrive\Documents\repos\pluginmanager
# sys.path.append("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")
import site
site.addsitedir("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")

import plugget
import plugget.commands as cmd
import plugget.apps.blender as b

from importlib import reload
reload(plugget)
reload(b)
reload(cmd)

cmd.install("textools")




## ============================================

#max
# import sys
#
# # C:\Users\hanne\OneDrive\Documents\repos\pluginmanager
# sys.path.append("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")
import site
site.addsitedir("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")

import plugget
import plugget.data as d
import plugget.commands as cmd
import plugget.actions.max_macroscript as ma
# import plugget.apps.blender as b

from importlib import reload

reload(plugget)
reload(d)
reload(cmd)
reload(ma)

import traceback

try:
    cmd.install("uv-copy")
except:

    traceback.print_exc()
