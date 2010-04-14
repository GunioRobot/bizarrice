import datetime
import re
import logging

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache
from blog import utils


class Publishable(polymodel.PolyModel): #{{{ Publishable Base Class
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    description = db.StringProperty() # Used as meta
    pub_date = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    author = db.UserProperty(auto_current_user_add=True)
    has_comments = False

    def update_markdown_fields(self):
        import import_wrapper
        import smartypants
        if not hasattr(self, 'markdown_map'):
            return
        for key, value in self.markdown_map:
            if not hasattr(self, key) or not hasattr(self, value):
                logging.error('AttributeError on markdown_map for class %s'
                              % self.__class__.__name__)
                continue
            if getattr(self, key) is not None:
                data = utils.markdown(getattr(self, key))
                data = smartypants.smartyPants(data)
                setattr(self, value, data)

    def test_slug_collision(self, limit_by_day=False):
        # Auto-filling slug field, if needed.
        if self.slug is None or len(self.slug.strip()) == 0:
            self.slug = self.title
        self.slug = utils.slugify(self.slug)

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
        key = super(Publishable, self).put()
        self.clear_cache()
        return key

    def get_absolute_url(self):
        raise NotImplementedError, ("get_absolute_url must be implemented for"
                                    " every Publishable model.")

    def clear_cache(self):
        memcache.delete('sitemap.xml')
#}}}

class Link(Publishable): #{{{ Link Model
    markdown_map = (
        ('body', 'body_html'),
    )
    body = db.TextProperty(required=True)
    body_html = db.TextProperty()
    url = db.LinkProperty(required=True)

    def _get_internal_url(self):
        # NOTE: this is *not* rendered
        return "/%04d/%02d/%02d/%s" % (self.pub_date.year,
                                       self.pub_date.month,
                                       self.pub_date.day,
                                       self.slug)

    def get_absolute_url(self):
        return "%s" % self.url

    def get_edit_url(self):
        if not self.is_saved():
            return '/admin/link/new'
        else:
            return "/admin/link/edit%s" % self._get_internal_url()

    def clear_cache(self):
        # Delete the cached archive list if we are saving a new link
        if not self.is_saved():
            memcache.delete('archive_list')
        memcache.delete('atom')
        memcache.delete('link_list')
        memcache.delete('link%s' % self._get_internal_url())
        super(Link, self).clear_cache()

    def put(self):
        self.test_slug_collision(limit_by_day=True)
        return super(Link, self).put()

    def __unicode__(self):
        ret = '<Link "%s", %s>' % (self.title, self.url)
        return ret.encode('utf8')
    __repr__ = __unicode__
#}}}

class Page(Publishable): #{{{ Page Model
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

    def clear_cache(self):
        memcache.delete('page_list')
        memcache.delete('page-%s' % self.slug)
        super(Page, self).clear_cache()

    def put(self):
        self.test_slug_collision(False)
        return super(Page, self).put()

    def __unicode__(self):
        ret = '<Page "%s", %s>' % (self.title,
                                   self.pub_date.strftime('%Y-%m-%d'))
        return ret.encode('utf8')
    __repr__ = __unicode__
#}}}

class Post(Publishable): #{{{ Post Model
    markdown_map = (
        ('body', 'body_html'),
        ('excerpt', 'excerpt_html'),
    )

    excerpt = db.TextProperty(default=None)
    body = db.TextProperty(required=True)
    excerpt_html = db.TextProperty(default=None)
    body_html = db.TextProperty()
    tags = db.StringListProperty()
    has_comments = True

    def get_absolute_url(self):
        return "/%04d/%02d/%02d/%s" % (self.pub_date.year,
                                       self.pub_date.month,
                                       self.pub_date.day,
                                       self.slug)

    def get_edit_url(self):
        return "/admin/post/edit%s" % self.get_absolute_url()

    def clear_cache(self):
        # Delete the cached archive list if we are saving a new post
        if not self.is_saved():
            memcache.delete('archive_list')
        # Delete the cached tag list whenever a post is created/updated
        memcache.delete('tag_list')
        memcache.delete('atom')
        memcache.delete('post%s' % self.get_absolute_url())
        super(Post, self).clear_cache()

    def _normalize_tags(self):
        # Split tags and ensure none is repeated.
        # The splitting is needed because we change the field
        # type for tags on controllers.admin.PostForm
        tags = ' '.join(self.tags).lower().split()
        tags = map(utils.slugify,list(set(tags)))
        self.tags = tags

    def put(self):
        self._normalize_tags()
        self.test_slug_collision(True)
        return super(Post, self).put()

    def __unicode__(self):
        ret = u'<Post "%s", %s>' % (self.title,
                                    self.pub_date.strftime('%Y-%m-%d'))
        return ret.encode('utf8')
    __repr__ = __unicode__
#}}}

class SlugConstraintViolation(Exception):
    def __init__(self, slug, date=None):
        msg_list = ['Slug "%s" is not unique' % slug]
        if date is not None:
            msg_list.append('for date "%s"' % date.date())
        super(SlugConstraintViolation, self).__init__(" ".join(msg_list))
