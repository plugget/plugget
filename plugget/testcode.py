import sys
# C:\Users\hanne\OneDrive\Documents\repos\pluginmanager
sys.path.append("C:\\Users\\hanne\\OneDrive\\Documents\\repos\\plugget")

import plugget
import plugget.commands as cmd
import plugget.apps.blender as b

from importlib import reload
reload(plugget)
reload(b)
reload(cmd)

print([x for x in cmd.search()])