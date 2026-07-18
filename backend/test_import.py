import importlib.util
filepath = "/home/emmanouil/Documents/Projects/MnApps/KeepMeUpdated Plugins/gotify.py"
module_name = "app.plugins.dynamic_plugin_gotify"
spec = importlib.util.spec_from_file_location(module_name, filepath)
module = importlib.util.module_from_spec(spec)
import sys
sys.path.insert(0, "/home/emmanouil/Documents/Projects/MnApps/KeepMeUpdated/backend")
try:
    spec.loader.exec_module(module)
    print("Success!")
except Exception as e:
    print("Error:", repr(e))
