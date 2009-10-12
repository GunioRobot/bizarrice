import os
import string
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from dateutil.relativedelta import *

import config
import helpers


class Page(object):
    def render(self, handler, template_file, template_values={}):
        """Render a template"""
        #archive_list = get_archive_list()
        #tag_list = get_tag_list()

        values = {
            #'archive_list': archive_list,
            #'tag_list': tag_list,
            'page_list': helpers.get_page_list(),
            'user': users.get_current_user(),
            'user_is_admin': users.is_current_user_admin(),
            'config': config,
        }

        values.update(template_values)

        template_path = os.path.join(config.APP_ROOT_DIR, template_file)
        handler.response.out.write(template.render(template_path, values))

    def render_paginated_query(self, handler, query, values_name,
                               template_file, template_values={}):
        """Paginate a query and render the requested page"""
        num = config.items_per_page
        offset = string.atoi(handler.request.get('offset') or str(0))

        items = query.fetch(num + 1, offset)

        values = {values_name: items}
        if len(items) > num:
            values.update({'next_offset': str(offset + num)})
            items.pop()
        if offset > 0:
            values.update({'prev_offset': str(offset - num)})
        template_values.update(values)

        self.render(handler, template_file, template_values)

    def render_error(self, handler, error):
        """Render an error page"""
        # TODO: Add more error pages for 403, 500, etc.
        valid_errors = [404]

        # If the error code given is not in the list then default to 404
        if error not in valid_errors:
            error = 404

        # Set the error code on the handler
        handler.error(error)

        self.render(handler, 'templates/error/%d.html' % error, {})
