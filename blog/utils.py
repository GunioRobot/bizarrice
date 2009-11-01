import view
import datetime
import blog

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache


def with_page(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, page_slug=None):
        page = None
        if page_slug is not None:
            page = get_page(page_slug)
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
            post = get_post(year, month, day, slug)
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
    import import_wrapper
    import_wrapper.fix_sys_path()
    from markdown import Markdown
    extensions = kwargs.pop('extensions', False) or ['extra', 'codehilite',
                                                     'toc']
    extensions += kwargs.pop('extra', [])
    md = Markdown(extensions=extensions, **kwargs)
    return md.convert(text)

def slugify(value):
    """
    Adapted from Django's django.template.defaultfilters.slugify.
    """
    import re
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def get_post(year, month, day, slug):
    cached_id = 'post/%s/%s/%s/%s' % (year, month, day, slug)
    post = memcache.get(cached_id)
    if post is None:
        year = int(year)
        month = int(month)
        day = int(day)

        # Build the time span to check for the given slug
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to check for slug uniqueness in the specified time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.filter('slug = ', slug)
        post = query.get()
        memcache.set(cached_id, post)
    return post

def get_page(slug):
    page = memcache.get('page-%s' % slug)
    if page is None:
        query = blog.Page.all()
        query.filter('slug = ', slug)
        page = query.get()
        memcache.set('page-%s' % slug, page)
    return page

def get_archive_list():
    """Return a list of the archive months and their article counts."""
    import import_wrapper
    import_wrapper.load_zip('dateutil')
    from dateutil.relativedelta import relativedelta

    # Attempt to get a memcache'd copy first
    archive = memcache.get('archive_list')
    if archive is not None:
        return archive

    # Get the date of the oldest post
    query = db.Query(blog.Post)
    query.order('pub_date')
    oldest = query.get()

    # Handle the situation where there are no posts
    if oldest is None:
        memcache.set('archive_list', [])
        return []

    # Create a date delta for moving ahead 1 month
    plus_one_month = relativedelta(months=+1)

    # Calculate the start and end dates for the archive
    start_date = datetime.date(oldest.pub_date.year, oldest.pub_date.month, 1)
    end_date = datetime.date.today()
    end_date = datetime.date(end_date.year, end_date.month, 1) + plus_one_month

    # Loop through each month in the time span and count the number
    # of posts made in that month
    archive = []
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + plus_one_month

        query = db.Query(blog.Post)
        query.filter('pub_date >= ', current_date)
        query.filter('pub_date < ', next_date)

        archive.append({
            'date': current_date,
            'count': query.count(1000),
            'url': '/%04d/%02d' % (current_date.year, current_date.month),
        })
        current_date = next_date

    memcache.set('archive_list', archive)
    return archive

def get_tag_list():
    """Return a list of the tags and their article counts"""
    # Attempt to get a memcache'd copy first
    tag_list = memcache.get('tag_list')
    if tag_list is not None:
        return tag_list

    # Build a list of tags and their article counts
    tag_list = {}
    query = blog.Post.all()
    for post in query:
        for tag in post.tags:
            if tag in tag_list:
                tag_list[tag] += 1
            else:
                tag_list[tag] = 1

    # Sort the tag dictionary by name into a list
    # and add each tag's URL
    sorted_tag_list = []
    for tag in sorted(tag_list.iterkeys()):
        sorted_tag_list.append({
            'tag': tag,
            'count': tag_list[tag],
            'url': '/tag/%s' % (tag),
        })

    memcache.set('tag_list', sorted_tag_list)
    return sorted_tag_list

def get_page_list():
    pages = memcache.get('page_list')
    if pages is not None:
        return pages

    page_list = []
    page_list = blog.Page.all().order('index').fetch(1000)
    memcache.set('page_list', page_list)
    return page_list
