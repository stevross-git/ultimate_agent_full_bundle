# ultimate_agent/config/__init__.py

from .settings import config  # ✅ correctly imported config dictionary

print(config['port'])  # ✅ now this will work
