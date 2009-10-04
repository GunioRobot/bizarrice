import datetime

from google.appengine.ext import webapp
from google.appengine.api import memcache

from models import blog
import view


class AdminHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'posts': blog.Post.all().order('-pub_date')
        }
        page = view.Page()
        page.render(self, 'templates/admin/index.html', template_values)


class CreatePageHandler(webapp.RequestHandler):
    def get(self):
        page = view.Page()
        page.render(self, 'templates/admin/page_form.html')

    def post(self):
        new_page = blog.Page()
        new_page.title = self.request.get('title')
        new_page.body = self.request.get('body')
        slug = self.request.get('slug').strip()
        if slug == '':
            slug = blog.slugify(new_post.title)
        new_page.slug = slug

        new_page.put()
        if self.request.get('submit') == 'Submit':
            self.redirect(new_post.get_absolute_url())
        else:
            template_values = {
                'page': new_page,
                }
            page = view.Page()
            page.render(self, 'templates/admin/page_form.html',
                        template_values)


class CreatePostHandler(webapp.RequestHandler):
    def get(self):
        page = view.Page()
        page.render(self, 'templates/admin/post_form.html')

    def post(self):
        new_post = blog.Post()
        new_post.title = self.request.get('title')
        new_post.body = self.request.get('body')

        slug = self.request.get('slug').strip()
        if slug == '':
            slug = blog.slugify(new_post.title)
        new_post.slug = slug

        excerpt = self.request.get('excerpt').strip()
        if excerpt == '':
            excerpt = None
        new_post.excerpt = excerpt

        new_post.tags = self.request.get('tags').split()

        new_post.put()
        if self.request.get('submit') == 'Submit':
            self.redirect(new_post.get_absolute_url())
        else:
            template_values = {
                'post': new_post,
            }
            page = view.Page()
            page.render(self, 'templates/admin/post_form.html',
                        template_values)


class EditPostHandler(webapp.RequestHandler):

    def get(self, year, month, day, slug):
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

        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            template_values = {
                'action': post.get_edit_url()
                'post': post,
            }

            page = view.Page()
            page.render(self, 'templates/admin/post_form.html', template_values)

    def post(self, year, month, day, slug):
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

        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            post.title = self.request.get('title')
            post.body = self.request.get('body')

            slug = self.request.get('slug').strip()
            if slug == '':
                slug = blog.slugify(post.title)
            post.slug = slug

            excerpt = self.request.get('excerpt').strip()
            if excerpt == '':
                excerpt = None
            post.excerpt = excerpt

            post.tags = self.request.get('tags').split()

            post.put()
            if self.request.get('submit') == 'Submit':
                self.redirect(post.get_absolute_url())
            else:
                template_values = {
                    'action': post.get_edit_url(),
                    'post': post,
                }
                page = view.Page()
                page.render(self, 'templates/admin/post_form.html',
                            template_values)


class ClearCacheHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()

