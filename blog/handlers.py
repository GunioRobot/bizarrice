import datetime
import config
import view
import helpers
import blog

from urlparse import urljoin
from google.appengine.ext import webapp
from google.appengine.api import memcache
from blog.utils import with_page, with_post


class IndexHandler(webapp.RequestHandler):
    def get(self):
        query = blog.Post.all()
        query.order('-pub_date')

        template_values = {
            'page_title': 'Home',
        }
        renderer = view.Renderer()
        renderer.render_paginated_query(self, query, 'posts',
                                        'blog/index.html',
                                        template_values)


class PageHandler(webapp.RequestHandler):
    @with_page
    def get(self, page):
        template_values = {
            'page': page,
        }
        renderer = view.Renderer()
        renderer.render(self, 'blog/page.html', template_values)


class PostHandler(webapp.RequestHandler):
    @with_post
    def get(self, post):
        template_values = {
            'post': post,
        }
        renderer = view.Renderer()
        renderer.render(self, 'blog/post.html', template_values)


class TagHandler(webapp.RequestHandler):
    def get(self, tag):
        query = blog.Post.all()
        query.filter('tags = ', tag)
        query.order('-pub_date')

        template_values = {
            'page_title': 'Posts tagged "%s"' % (tag),
            'page_description': 'Posts tagged "%s"' % (tag),
        }

        renderer = view.Renderer()
        renderer.render_paginated_query(self, query, 'posts',
                                        'blog/index.html',
                                        template_values)


class YearHandler(webapp.RequestHandler):
    def get(self, year):
        year = int(year)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, 1, 1)
        end_date = datetime.datetime(year + 1, 1, 1)

        # Create a query to find posts in the given time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        template_values = {
            'page_title': 'Yearly Post Archive: %d' % (year),
            'page_description': 'Yearly Post Archive: %d' % (year),
        }

        renderer = view.Renderer()
        renderer.render_paginated_query(self, query, 'posts',
                                        'blog/index.html',
                                        template_values)


class MonthHandler(webapp.RequestHandler):
    def get(self, year, month):
        year = int(year)
        month = int(month)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, month, 1)
        end_year = year if month < 12 else year + 1
        end_month = month + 1 if month < 12 else 1
        end_date = datetime.datetime(end_year, end_month, 1)

        # Create a query to find posts in the given time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        month_text = start_date.strftime('%B %Y')
        template_values = {
            'page_title': 'Monthly Post Archive: %s' % (month_text),
            'page_description': 'Monthly Post Archive: %s' % (month_text),
        }

        renderer = view.Renderer()
        renderer.render_paginated_query(self, query, 'posts',
                                        'blog/index.html',
                                        template_values)


class DayHandler(webapp.RequestHandler):
    def get(self, year, month, day):
        year = int(year)
        month = int(month)
        day = int(day)

        # Build the time span to check for posts
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to find posts in the given time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.order('-pub_date')

        day_text = start_date.strftime('%x')
        template_values = {
            'page_title': 'Daily Post Archive: %s' % (day_text),
            'page_description': 'Daily Post Archive: %s' % (day_text),
        }

        renderer = view.Renderer()
        renderer.render_paginated_query(self, query, 'posts',
                                        'blog/index.html',
                                        template_values)


class FeedburnerHandler(webapp.RequestHandler):
    def get(self):
        if not config.feedburner:
            self.redirect("/atom.xml", permanent=True)
        else:
            self.redirect("http://feeds.feedburner.com/caioromao",
                          permanent=True)


class AtomHandler(webapp.RequestHandler):
    def get(self):
        template_values = memcache.get('atom')
        if template_values is None:
            query = blog.Post.all().order('-pub_date')
            posts = query.fetch(10)
            template_values = {
                'posts': posts,
                'updated': posts[0].updated,
            }
            memcache.set('atom', template_values)
        renderer = view.Renderer()
        self.response.headers["Content-Type"] = "application/atom+xml"
        renderer.render(self, 'blog/atom.xml', template_values)

