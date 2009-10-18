import sys
import glob
import os
import config
# This assumes that you don't have the app-engine stuff in your import path by default.
try:
    import google

except ImportError, e:
    # Don't show warnings for libs found in the apps lib directory that are also
    #  installed in site-packages or via setuptools.
    import warnings
    warnings.filterwarnings('ignore',
                            message=r'Module .*? is being added to sys.path', append=True)
    # Make the appengine libs available if we want to use ipython or something.
    sys.path.append('/opt/google-appengine/')
    sys.path.append('/opt/google-appengine/lib/yaml/')
    sys.path.append('/opt/google-appengine/lib/webob/')

root = config.APP_ROOT_DIR

sys.path.append(os.path.join(root, 'lib'))
for ziplib_fn in glob.glob(os.path.join(root, 'lib/zip', '*.zip')):
    sys.path.append(ziplib_fn)
