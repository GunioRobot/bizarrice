#!/usr/bin/env python

import import_wrapper
import config
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from admin.handlers import *


def main():
    # Load custom template filters:
    webapp.template.register_template_library('filters')
    application = webapp.WSGIApplication(
        [('/admin/', AdminHandler),
         ('/admin/clear-cache', ClearCacheHandler),
         ('/admin/post/new', PostHandler),
         ('/admin/post/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          PostHandler),
         ('/admin/post/delete/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          DeletePostHandler),
         ('/admin/link/new', LinkHandler),
         ('/admin/link/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          LinkHandler),
         ('/admin/link/delete/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          DeleteLinkHandler),
         ('/admin/page/new', PageHandler),
         ('/admin/page/edit/([-\w]+)', PageHandler),
         ('/admin/page/delete/([-\w]+)', DeletePageHandler),
        ], debug=config.debug)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    import_wrapper.fix_sys_path()
    main()
