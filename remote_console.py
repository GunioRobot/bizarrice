#!/usr/bin/python2.5

"""A remote_api activated console for Bizarrice."""

import code
import os
import re
import sys
import logging

# useful local modules
import import_wrapper
import config
import dateutil
import blog
import admin


from getpass import getpass
from optparse import OptionParser, OptionValueError


username = ''
password = ''

def setup_gae():
    """Hardwiring GAE libraries to the import path."""
    gaepath = re.compile(r'google[-_]appengine')
    for path in os.environ['PATH'].split(':'):
        if gaepath.search(path):
            sys.path.append(path)
            sys.path.append('%s/lib/yaml/lib/' % path)
            break

def setup(email, passwd, domain, app):
    global username
    global password
    username = email
    password = passwd
    if email is None or len(email) == 0:
        raise OptionValueError, ('You need to supply the administrator '
                                 'e-mail address.')
    if app is None or len(app) == 0:
        raise OptionValueError, ('You need to supply a valid app name'
                                 ' (the same one from app.yaml)')
    os.environ['AUTH_DOMAIN'] = domain
    os.environ['USER_EMAIL'] = email
    # loading appengine modules
    setup_gae()
    from google.appengine.ext import db
    from google.appengine.ext.remote_api import remote_api_stub
    remote_api_stub.ConfigureRemoteDatastore(app, '/remote_api', auth_func)


attempts = 0
def auth_func():
    global attempts
    global username
    global password
    attempts += 1
    if attempts == 2:
        password = None
    if attempts > 2:
        username = None
        password = None
    if username is None or len(username) == 0:
        username = raw_input('Username: ')
    if password is None or len(password) == 0:
        password = getpass('Password: ')
    return (username, password)

def read_options():
    parser = OptionParser()
    parser.add_option('-u', '--username', dest='email')
    parser.add_option('-p', '--password', dest='passwd')
    parser.add_option('-d', '--domain', dest='domain', default='gmail.com')
    parser.add_option('-a', '--app', dest='app')
    options, args = parser.parse_args()
    return options.__dict__

if __name__ == '__main__':
    options = read_options()
    setup(**options)
    code.interact('AppEngine interactive console for %s' % options['app'], None, locals())


