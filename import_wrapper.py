import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

def setup_gae_dev():
    """Sets up PYTHONPATH to allow importing gae modules."""
    try:
        import google
    except ImportError:
        import re
        gaepath = re.compile(r'google[-_]appengine')
        for path in os.environ['PATH'].split(':'):
            if gaepath.search(path):
                sys.path.append(path)
                sys.path.append(os.path.join(path, 'lib/yaml/lib'))
                sys.path.append(os.path.join(path, 'lib/webob'))
                sys.path.append(os.path.join(path, 'lib/django'))
                break

def load_zip(modulename):
    """Enables importing the module `modulename` at lib/zip/."""
    zipfile = '%s.zip' % modulename
    path = os.path.join(os.path.dirname(__file__), 'lib/zip/', zipfile)
    sys.path.append(path)

# from Nick's bloggart
# see issue772: http://code.google.com/p/googleappengine/issues/detail?id=772
ultimate_sys_path = None

def fix_sys_path():
    global ultimate_sys_path
    if ultimate_sys_path is None:
        ultimate_sys_path = list(sys.path)
    else:
        sys.path[:] = ultimate_sys_path
