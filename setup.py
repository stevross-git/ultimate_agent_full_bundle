import os, runpy

# Delegate to package setup script
PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'ultimate_agent')
os.chdir(PACKAGE_DIR)
runpy.run_path('setup.py', run_name='__main__')
