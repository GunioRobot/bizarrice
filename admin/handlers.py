import view
import helpers
import config
import logging

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import blog


class AdminHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'posts': blog.Post.all().order('-pub_date'),
            'pages': blog.Page.all().order('index'),
        }
        page = view.Page()
        page.render(self, 'templates/admin/index.html', template_values)


class ClearCacheHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/admin/')


#{{{ Page Handlers
def with_page(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, page_slug=None):
        page = None
        if page_slug is not None:
            page = helpers.get_page(page_slug)
            if page is None:
                view.Page().render_error(self, 404)
                return
        funct(self, page)
    return decorate

class PageHandler(webapp.RequestHandler):
    def render_form(self, page=None, form=None):
        template_values = {
            'page': page,
            'form': form,
        }
        renderer = view.Page()
        renderer.render(self, 'templates/admin/page_form.html',
                        template_values)

    @with_page
    def get(self, page):
        self.render_form(page, blog.PageForm(instance=page))

    @with_page
    def post(self, page):
        form = blog.PageForm(data=self.request.POST, instance=page)
        if self.request.get('submit') == 'Submit' and form.is_valid():
            page = form.save(commit=False)
            try:
                page.put()
            except blog.models.SlugConstraintViolation:
                logging.error('Slug "%s" is not unique' % page.slug)
                self.render_form(page, form)
            else:
                self.redirect(page.get_absolute_url())
        else:
            if form.is_valid():
                page = form.save(commit=False)
                page.update_markdown_fields()
            self.render_form(page, form)


class DeletePageHandler(webapp.RequestHandler):
    def get(self, slug):
        p = helpers.get_page(slug)
        if p is not None:
            p.delete()
        memcache.flush_all()
        self.redirect(config.url)
#}}}

#{{{ Post Handlers
def with_post(funct):
    """Credits: http://blog.notdot.net/"""
    def decorate(self, year=None, month=None, day=None, slug=None):
        post = None
        if slug is not None:
            post = helpers.get_post(year, month, day, slug)
            if post is None:
                view.Page().render_error(self, 404)
                return
        funct(self, post)
    return decorate

class PostHandler(webapp.RequestHandler):
    def render_form(self, post=None, form=None):
        template_values = {
            'post': post,
            'form': form,
        }
        renderer = view.Page()
        renderer.render(self, 'templates/admin/post_form.html',
                        template_values)

    @with_post
    def get(self, post):
        self.render_form(post, blog.PostForm(instance=post))

    @with_post
    def post(self, post):
        form = blog.PostForm(data=self.request.POST, instance=post)
        if self.request.get('submit') == 'Submit' and form.is_valid():
            post = form.save(commit=False)
            try:
                post.put()
            except blog.models.SlugConstraintViolation:
                logging.error('Slug "%s" is not unique' % post.slug)
                # TODO: provide error feedback through a rails-like flash
                self.render_form(post, form)
            else:
                self.redirect(post.get_absolute_url())
        else:
            if form.is_valid():
                post = form.save(commit=False)
                post.update_markdown_fields()
            self.render_form(post, form)


class DeletePostHandler(webapp.RequestHandler):
    def get(self, year, month, day, slug):
        p = helpers.get_post(year, month, day, slug)
        if p is not None:
            p.delete()
        memcache.flush_all()
        self.redirect(config.url)

#}}}


