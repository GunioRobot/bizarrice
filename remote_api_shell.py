#!/usr/bin/python2.5
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""An interactive python shell that uses remote_api.

Usage:
  remote_api_shell.py [-s HOSTNAME] APPID [PATH]
"""


import atexit
import code
import getpass
import optparse
import os
import sys
import re

try:
    import readline
except ImportError:
    readline = None

import import_wrapper
import_wrapper.setup_gae_dev()

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.api import datastore
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import search


HISTORY_PATH = os.path.expanduser('~/.remote_api_shell_history')
DEFAULT_PATH = '/remote_api'
BANNER = """App Engine remote_api shell
Python %s
The db, users, urlfetch, and memcache modules are imported.""" % sys.version


def auth_func():
    return (raw_input('Email: '), getpass.getpass('Password: '))


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('-s', '--server', dest='server',
                      help='The hostname your app is deployed on. '
                           'Defaults to <app_id>.appspot.com.')
    (options, args) = parser.parse_args()

    if not args or len(args) > 2:
        import sys
        print >> sys.stderr, __doc__
        if len(args) > 2:
          print >> sys.stderr, 'Unexpected arguments: %s' % args[2:]
        sys.exit(1)

    appid = args[0]
    if len(args) == 2:
        path = args[1]
    else:
        path = DEFAULT_PATH

    remote_api_stub.ConfigureRemoteApi(appid, path, auth_func,
                                       servername=options.server)
    remote_api_stub.MaybeInvokeAuthentication()

    import os
    os.environ['SERVER_SOFTWARE'] = 'Development (remote_api_shell)/1.0'
    # Import the 'see' helper, if it's available
    try:
        from see import see
    except ImportError:
        pass

    # Make sure modules in the current directory can't interfere

    try:
        import readline
    except ImportError:
        import sys
        print >> sys.stderr, 'readline unavailable - tab completion disabled.'
    else:
        import rlcompleter

        class TabCompleter(rlcompleter.Completer):
            """Completer that supports indenting"""

            def complete(self, text, state):
                if not text:
                    return ('    ', None)[state]
                else:
                    return rlcompleter.Completer.complete(self, text, state)

        readline.parse_and_bind('tab: complete')
        readline.set_completer(TabCompleter().complete)

        import atexit
        import os

        history_path = os.path.expanduser(HISTORY_PATH)
        atexit.register(lambda: readline.write_history_file(history_path))
        if os.path.isfile(history_path):
            readline.read_history_file(history_path)

    try:
        _pythonrc()
        del _pythonrc
    except:
        pass


    import sys
    sys.ps1 = '%s> ' % appid
    sys.ps2 = '%s| ' % re.sub('\w', ' ', appid)

    code.interact(banner=BANNER, local=globals())

def _pythonrc():
    # Enable readline, tab completion, and history

    # Pretty print evaluated expressions

    try:
        import __builtin__
        IS_PY3K = False
    except:
        import builtins as __builtin__
        IS_PY3K = True
    import pprint
    import pydoc
    import sys
    import types

    if IS_PY3K:
        help_types = (types.BuiltinFunctionType, types.BuiltinMethodType,
                      types.FunctionType, types.MethodType, types.ModuleType,
                      # method_descriptor
                      type(list.remove))
    else:
        help_types = (types.BuiltinFunctionType, types.BuiltinMethodType,
                      types.FunctionType, types.MethodType, types.ModuleType,
                      types.TypeType, types.UnboundMethodType,
                      # method_descriptor
                      type(list.remove))

    def formatargs(func):
        """Returns a string representing a function's argument specification,
        as if it were from source code.

        For example:

        >>> class Foo(object):
        ...     def bar(self, x=1, *y, **z):
        ...         pass
        ...
        >>> formatargs(Foo.bar)
        'self, x=1, *y, **z'
        """

        from inspect import getargspec
        args, varargs, varkw, defs = getargspec(func)

        # Fill in default values
        if defs:
            last = len(args) - 1
            for i, val in enumerate(reversed(defs)):
                args[last - i] = '%s=%r' % (args[last - i], val)

        # Fill in variable arguments
        if varargs:
            args.append('*%s' % varargs)
        if varkw:
            args.append('**%s' % varkw)

        return ', '.join(args)

    def _ioctl_width(fd):

        from fcntl import ioctl
        from struct import pack, unpack
        from termios import TIOCGWINSZ
        return unpack('HHHH',
                      ioctl(fd, TIOCGWINSZ, pack('HHHH', 0, 0, 0, 0)))[1]

    def get_width():
        """Returns terminal width"""

        width = 0
        try:
            width = _ioctl_width(0) or _ioctl_width(1) or _ioctl_width(2)
        except ImportError:
            pass
        if not width:
            import os
            width = os.environ.get('COLUMNS', 0)
        return width

    def pprinthook(value):
        """Pretty print an object to sys.stdout and also save it in
        __builtin__.
        """

        if value is None:
            return
        __builtin__._ = value

        if isinstance(value, help_types):
            reprstr = repr(value)
            if hasattr(value, 'func_code') or hasattr(value, 'im_func'):
                parts = reprstr.split(' ')
                parts[1] = '%s(%s)' % (parts[1], formatargs(value))
                reprstr = ' '.join(parts)
            print(reprstr)
            if getattr(value, '__doc__', None):
                print()
                print(pydoc.getdoc(value))
        else:
            pprint.pprint(value, width=get_width() or 80)

    sys.displayhook = pprinthook

    try:
        if sys.platform == 'win32':
            raise ImportError()
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        from pygments import highlight
        from pygments.lexers import PythonTracebackLexer
        from pygments.formatters import TerminalFormatter

        _old_excepthook = sys.excepthook
        def excepthook(exctype, value, traceback):
            """Prints exceptions to sys.stderr and colorizes them"""

            # traceback.format_exception() isn't used because it's
            # inconsistent with the built-in formatter
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            try:
                _old_excepthook(exctype, value, traceback)
                s = sys.stderr.getvalue()
                s = highlight(s, PythonTracebackLexer(), TerminalFormatter())
                old_stderr.write(s)
            finally:
                sys.stderr = old_stderr

        sys.excepthook = excepthook
    except ImportError:
        pass


def source(obj):
    """Displays the source code of an object.

    Applies syntax highlighting if Pygments is available.
    """

    import sys

    from inspect import findsource, getmodule, getsource, getsourcefile
    try:
        # Check to see if the object is defined in a shared library, which
        # findsource() doesn't do properly (see issue4050)
        if not getsourcefile(obj):
            raise TypeError()
        s = getsource(obj)
    except TypeError:
        __trash__ = sys.stderr.write("Source code unavailable (maybe it's "
                                     "part of a C extension?\n")
        return

    import re
    enc = 'ascii'
    for line in findsource(getmodule(obj))[0][:2]:
        m = re.search(r'coding[:=]\s*([-\w.]+)', line)
        if m:
            enc = m.group(1)
    try:
        s = s.decode(enc, 'replace')
    except LookupError:
        s = s.decode('ascii', 'replace')

    try:
        if sys.platform == 'win32':
            raise ImportError()
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import TerminalFormatter
        s = highlight(s, PythonLexer(), TerminalFormatter())
    except (ImportError, UnicodeError):
        pass

    import os
    from pydoc import pager
    has_lessopts = 'LESS' in os.environ
    lessopts = os.environ.get('LESS', '')
    try:
        os.environ['LESS'] = lessopts + ' -R'
        pager(s.encode(sys.stdout.encoding, 'replace'))
    finally:
        if has_lessopts:
            os.environ['LESS'] = lessopts
        else:
            os.environ.pop('LESS', None)

if __name__ == '__main__':
  main(sys.argv)
