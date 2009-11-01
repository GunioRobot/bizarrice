import os
import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from django.template import TemplateDoesNotExist

import blog
import config


class Renderer(object):
    def theme_template(self, path, values):
        theme = config.theme or 'default'
        base_path = os.path.join(config.APP_ROOT_DIR, 'themes')
        template_path = os.path.join(base_path, theme, path)
        try:
            templ = template.render(template_path, values)
        except TemplateDoesNotExist:
            logging.error('Template "%s" for theme "%s" does not exist.'
                          % (path, theme))
            template_path = os.path.join(base_path, 'default', path)
            templ = template.render(template_path, values)
        return templ

    def render(self, handler, template_file, template_values={}):
        values = {
            'page_list': blog.utils.get_page_list(),
            'user': users.get_current_user(),
            'user_is_admin': users.is_current_user_admin(),
            'config': config,
        }

        values.update(template_values)
        handler.response.out.write(self.theme_template(template_file,
                                                       values))

    def render_paginated_query(self, handler, query, values_name,
                               template_file, template_values={}):
        """Paginate a query and render the requested page"""
        num = config.items_per_page
        page = int(handler.request.get('page', 0))
        offset = (page * num) if page > 0 else 0

        items = query.fetch(num + 1, offset)

        values = {values_name: items}
        if len(items) > num:
            values.update({'prev_page': str(page + 1)})
            items.pop()
        if offset > 0:
            values.update({'next_page': str(page - 1)})
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

        self.render(handler, 'error/%d.html' % error, {})
