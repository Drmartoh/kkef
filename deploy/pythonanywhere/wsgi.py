"""
PythonAnywhere WSGI entry point.

In the Web tab, set:
  Source code:  /home/<YOUR_PA_USERNAME>/kkef
  Working dir:  /home/<YOUR_PA_USERNAME>/kkef
  WSGI file:    /home/<YOUR_PA_USERNAME>/kkef/deploy/pythonanywhere/wsgi.py

Replace <YOUR_PA_USERNAME> below, then reload the web app.
"""
import os
import sys
from pathlib import Path

# Set PA_USERNAME in the Web tab "Environment variables" or edit the default below.
PA_USERNAME = os.environ.get("PA_USERNAME", "<YOUR_PA_USERNAME>")
if PA_USERNAME.startswith("<"):
    raise RuntimeError("Set PA_USERNAME to your PythonAnywhere username (Web tab or wsgi.py).")

PROJECT_HOME = Path(f"/home/{PA_USERNAME}/kkef")
if str(PROJECT_HOME) not in sys.path:
    sys.path.insert(0, str(PROJECT_HOME))

os.chdir(PROJECT_HOME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
