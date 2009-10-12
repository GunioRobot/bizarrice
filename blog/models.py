import import_wrapper
import datetime
import re
import logging
import smartypants
from markdown2 import markdown

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache


def slugify(value):
    """
    Adapted from Django's django.template.defaultfilters.slugify.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

class Publishable(polymodel.PolyModel):
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    pub_date = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    author = db.UserProperty(auto_current_user_add=True)

    def update_markdown_fields(self):
        if not hasattr(self, 'markdown_map'):
            return
        for key, value in self.markdown_map:
            if not hasattr(self, key) or not hasattr(self, value):
                logging.error('AttributeError on markdown_map for class %s'
                              % self.__class__.__name__)
                continue
            if getattr(self, key) is not None:
                data = markdown(getattr(self, key), extras=['code-color',
                                                            'footnotes'])
                data = smartypants.smartyPants(data)
                setattr(self, value, data)

    def test_slug_collision(self, limit_by_day=False):
        # Auto-filling slug field, if needed.
        if self.slug is None or len(self.slug.strip()) == 0:
            self.slug = self.title
        self.slug = slugify(self.slug)

        # Create a query to check for slug uniqueness
        query = self.all(keys_only=True)
        start_date = None
        if limit_by_day:
            # Build the time span to check for slug uniqueness
            start_date = datetime.datetime(self.pub_date.year,
                                           self.pub_date.month,
                                           self.pub_date.day)
            time_delta = datetime.timedelta(days=1)
            end_date = start_date + time_delta
            query.filter('pub_date >= ', start_date)
            query.filter('pub_date < ', end_date)
        query.filter('slug = ', self.slug)

        # Get the number of slug matches
        count = query.count(1)

        # If any slug matches were found then an exception should be raised
        if count == 1 and not self.is_saved():
            raise SlugConstraintViolation(self.slug, start_date)

    def put(self):
        self.update_markdown_fields()
        return super(Publishable, self).put()


class Page(Publishable):
    markdown_map = (
        ('body', 'body_html'),
    )

    body = db.TextProperty(required=True)
    body_html = db.TextProperty()
    # The order in which it'll be listed
    index = db.IntegerProperty()

    def get_absolute_url(self):
        return "/%s" % self.slug

    def get_edit_url(self):
        if not self.is_saved():
            return '/admin/page/new'
        else:
            return "/admin/page/edit%s" % self.get_absolute_url()

    def put(self):
        memcache.delete('page_list')
        self.test_slug_collision(False)
        memcache.delete('page-%s' % self.slug)
        return super(Page, self).put()


class Post(Publishable):
    markdown_map = (
        ('body', 'body_html'),
        ('excerpt', 'excerpt_html'),
    )

    excerpt = db.TextProperty(default=None)
    body = db.TextProperty(required=True)
    excerpt_html = db.TextProperty(default=None)
    body_html = db.TextProperty()
    tags = db.StringListProperty()

    def get_absolute_url(self):
        return "/%04d/%02d/%02d/%s" % (self.pub_date.year,
                                       self.pub_date.month,
                                       self.pub_date.day,
                                       self.slug)

    def get_edit_url(self):
        return "/admin/post/edit%s" % self.get_absolute_url()

    def put(self):
        # Delete the cached archive list if we are saving a new post
        if not self.is_saved():
            memcache.delete('archive_list')
        # Delete the cached tag list whenever a post is created/updated
        memcache.delete('tag_list')
        memcache.delete('atom')

        # Split tags and ensure none is repeated.
        # The splitting is needed because we change the field
        # type for tags on controllers.admin.PostForm
        tags = ' '.join(self.tags).split()
        tags = list(set(tags))
        self.tags = tags

        self.test_slug_collision(True)
        memcache.delete('post-%s' % self.slug)
        return super(Post, self).put()


class SlugConstraintViolation(Exception):
    def __init__(self, slug, date=None):
        msg_list = ['Slug "%s" is not unique' % slug]
        if date is not None:
            msg_list.append('for date "%s"' % date.date())
        super(SlugConstraintViolation, self).__init__(" ".join(msg_list))
