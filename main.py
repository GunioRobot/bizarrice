#!/usr/bin/env python

import config
import os
import sys

import import_wrapper
import wsgiref.handlers
from google.appengine.ext import webapp
from controllers import blog, admin, error


def main():
    # Load custom template filters:
    webapp.template.register_template_library('filters')
    application = webapp.WSGIApplication(
        [('/', blog.IndexHandler),
         ('/feed', blog.FeedburnerHandler),
         ('/atom.xml', blog.AtomHandler),
         ('/tag/([-\w]+)', blog.TagHandler),
         ('/(\d{4})', blog.YearHandler),
         ('/(\d{4})/(\d{2})', blog.MonthHandler),
         ('/(\d{4})/(\d{2})/(\d{2})', blog.DayHandler),
         ('/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', blog.PostHandler),
         ('/(\d{4})/(\d{2})/(\d{2})/([-\w]+).html', blog.PostHandler),
         ('/admin/?', admin.AdminHandler),
         ('/admin/clear-cache', admin.ClearCacheHandler),
         ('/admin/post/new', admin.CreatePostHandler),
         ('/admin/post/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          admin.EditPostHandler),
         ('/admin/page/new', admin.CreatePageHandler),
         ('/admin/page/edit/([-\w]+)', admin.EditPageHandler),
         ('/admin/delete/post/(\d{4})/(\d{2})/(\d{2})/([-\w]+)',
          admin.DeletePostHandler),
         ('/admin/delete/page/([-\w]+)', admin.DeletePageHandler),
         ('/([-\w]+)', blog.PageHandler),
         # If we make it this far then the page we are looking
         # for does not exist
         ('/.*', error.Error404Handler),
        ], debug=config.debug)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
