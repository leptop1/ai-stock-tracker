import os, sys
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("backend_app", os.path.join(backend_dir, "app.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app
