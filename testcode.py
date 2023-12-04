# import sys
# C:\Users\hanne\OneDrive\Documents\repos\pluginmanager
# sys.path.append("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")
import site
site.addsitedir("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")
site.addsitedir("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\detect-app")

import plugget
import plugget.commands as cmd
import plugget.data as da
import plugget.actions.blender_addon as ba

from importlib import reload
reload(plugget)
# reload(b)
reload(cmd)
reload(da)
reload(ba)

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
import plugget.actions.max3ds_macroscript as ma

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
