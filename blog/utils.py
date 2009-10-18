import config
import logging
import helpers
import view
import re

import pygments
from markdown import Markdown


def with_page(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, page_slug=None):
        page = None
        if page_slug is not None:
            page = helpers.get_page(page_slug)
            if page is None:
                view.Renderer().render_error(self, 404)
                return
        funct(self, page)
    return decorate

def with_post(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, year=None, month=None, day=None, slug=None):
        post = None
        if slug is not None:
            post = helpers.get_post(year, month, day, slug)
            if post is None:
                view.Renderer().render_error(self, 404)
                return
        funct(self, post)
    return decorate

def markdown(text, **kwargs):
    """Converts given `text` to html using python-markdown.

    This is meant to centralize markdown usage throughout Bizarrice.
    Keyword list arguments:
        * extensions: replaces every preset extension for the ones given.
        * extra: appends given extensions to the preset list.
    Every other initialization keyword argument for python-markdown is
    accepted and passed without validation. Use with care."""
    extensions = kwargs.pop('extensions', False) or ['extra', 'codehilite',
                                                     'toc']
    extensions += kwargs.pop('extra', [])
    md = Markdown(extensions=extensions, **kwargs)
    return md.convert(text)

def slugify(value):
    """
    Adapted from Django's django.template.defaultfilters.slugify.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
