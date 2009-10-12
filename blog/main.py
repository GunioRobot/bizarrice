#!/usr/bin/env python

import import_wrapper

import config
import error
import wsgiref.handlers

from google.appengine.ext import webapp
from blog.handlers import *


def main():
    # Load custom template filters:
    webapp.template.register_template_library('filters')
    application = webapp.WSGIApplication(
        [('/', IndexHandler),
         ('/feed', FeedburnerHandler),
         ('/atom.xml', AtomHandler),
         ('/tag/([-\w]+)', TagHandler),
         ('/([-\w]+)', PageHandler),
         ('/(\d{4})', YearHandler),
         ('/(\d{4})/(\d{2})', MonthHandler),
         ('/(\d{4})/(\d{2})/(\d{2})', DayHandler),
         ('/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', PostHandler),
         ('/(\d{4})/(\d{2})/(\d{2})/([-\w]+).html', PostHandler),
         # If we make it this far then the page we are looking
         # for does not exist
         ('/.*', error.Error404Handler),
        ], debug=config.debug)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
