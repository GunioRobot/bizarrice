import view
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
            'links': blog.Link.all().order('-pub_date'),
        }
        renderer = view.Renderer()
        renderer.render(self, 'admin/index.html',
                        template_values)


class ClearCacheHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/admin/')


#{{{ Page Handlers
class PageHandler(webapp.RequestHandler):
    def render_form(self, page=None, form=None):
        template_values = {
            'page': page,
            'form': form,
        }
        renderer = view.Renderer()
        renderer.render(self, 'admin/page_form.html',
                        template_values)

    @blog.utils.with_page
    def get(self, page):
        self.render_form(page, blog.PageForm(instance=page))

    @blog.utils.with_page
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
    @blog.utils.with_page
    def get(self, page):
        page.delete()
        memcache.flush_all()
        self.redirect('/admin/')
#}}}

#{{{ Post Handlers
class PostHandler(webapp.RequestHandler):
    def render_form(self, post=None, form=None):
        template_values = {
            'post': post,
            'form': form,
        }
        renderer = view.Renderer()
        renderer.render(self, 'admin/post_form.html',
                        template_values)

    @blog.utils.with_post
    def get(self, post):
        self.render_form(post, blog.PostForm(instance=post))

    @blog.utils.with_post
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
                blog.helpers.ping_services()
                self.redirect(post.get_absolute_url())
        else:
            if form.is_valid():
                post = form.save(commit=False)
                post.update_markdown_fields()
            self.render_form(post, form)


class DeletePostHandler(webapp.RequestHandler):
    @blog.utils.with_post
    def get(self, post):
        post.delete()
        memcache.flush_all()
        self.redirect('/admin/')
#}}}

#{{{ Link Handlers
class LinkHandler(webapp.RequestHandler):
    def render_form(self, link=None, form=None):
        template_values = {
            'link': link,
            'form': form,
        }
        renderer = view.Renderer()
        renderer.render(self, 'admin/link_form.html',
                        template_values)

    @blog.utils.with_link
    def get(self, link):
        self.render_form(link, blog.LinkForm(instance=link))

    @blog.utils.with_link
    def post(self, link):
        form = blog.LinkForm(data=self.request.POST, instance=link)
        if self.request.get('submit') == 'Submit' and form.is_valid():
            link = form.save(commit=False)
            try:
                link.put()
            except blog.models.SlugConstraintViolation:
                logging.error('Slug "%s" is not unique' % link.slug)
                # TODO: provide error feedback through a rails-like flash
                self.render_form(link, form)
            else:
                blog.helpers.ping_services()
                self.redirect(config.url)
        else:
            if form.is_valid():
                link = form.save(commit=False)
                link.update_markdown_fields()
            self.render_form(link, form)


class DeleteLinkHandler(webapp.RequestHandler):
    @blog.utils.with_link
    def get(self, link):
        link.delete()
        memcache.flush_all()
        self.redirect('/admin/')
#}}}
