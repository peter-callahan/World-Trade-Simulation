import os
import sys
import inspect

from subprocess import run

def get_script_dir(follow_symlinks=True):
    # https://stackoverflow.com/questions/3718657/how-do-you-properly-determine-the-current-script-directory/22881871#22881871

    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

#https://stackoverflow.com/questions/30076185/calling-a-python-script-with-input-within-a-python-script-using-subprocess
script_path = os.path.join(get_script_dir(), 'tradesim.py')

for x in range(0, 25):
    output = run([sys.executable, script_path],
                        input='\n'.join(['query 1', 'query 2']),
                        universal_newlines=True)