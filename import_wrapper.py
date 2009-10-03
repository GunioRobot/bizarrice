import sys
import glob
import os
# This assumes that you don't have the app-engine stuff in your import path by default.
try:
    import google
    
    # We don't need to worry since the pwd will be the same as __file__.
    root = ''
except ImportError, e:
    # Don't show warnings for libs found in the apps lib directory that are also
    #  installed in site-packages or via setuptools.
    import warnings
    warnings.filterwarnings('ignore',
                            message=r'Module .*? is being added to sys.path', append=True)
    # Make the appengine libs available if we want to use ipython or something.
    sys.path.insert(0, '/opt/google-appengine/')
    sys.path.insert(0, '/opt/google-appengine/lib/yaml/')
    # We need to use __file__ to find the absolute path to the apps lib/ directory
    root = os.path.split(__file__)[0]
sys.path.insert(0, os.path.join(root, 'lib'))
for ziplib_fn in glob.glob(os.path.join(root, 'lib/zip', '*.zip')):
    sys.path.insert(0, ziplib_fn)
