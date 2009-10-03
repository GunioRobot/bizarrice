#!/usr/bin/env python

import config
import os
import sys

import import_wrapper
import wsgiref.handlers
from google.appengine.ext import webapp
from handlers import blog, admin, error


def main():
    application = webapp.WSGIApplication(
        [('/', blog.IndexHandler),
         ('/feed', blog.RSS2Handler),
         ('/tag/([-\w]+)', blog.TagHandler),
         ('/(\d{4})', blog.YearHandler),
         ('/(\d{4})/(\d{2})', blog.MonthHandler),
         ('/(\d{4})/(\d{2})/(\d{2})', blog.DayHandler),
         ('/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', blog.PostHandler),
         ('/admin', admin.AdminHandler),
         ('/admin/clear-cache', admin.ClearCacheHandler),
         ('/admin/post/new', admin.CreatePostHandler),
         ('/admin/post/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          admin.EditPostHandler),
         # If we make it this far then the page we are looking
         # for does not exist
         ('/.*', error.Error404Handler),
        ], debug=config.SETTINGS.get('debug', False))
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
