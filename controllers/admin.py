import view
import helpers
import config
import logging

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from models import blog


class AdminHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'posts': blog.Post.all().order('-pub_date'),
            'pages': blog.Page.all().order('index'),
        }
        page = view.Page()
        page.render(self, 'templates/admin/index.html', template_values)

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

class PageForm(djangoforms.ModelForm):
    class Meta():
        model = blog.Page
        exclude = ['body_html', '_class', 'author', 'pub_date', 'updated']


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
        self.render_form(page, PageForm(instance=page))

    @with_page
    def post(self, page):
        form = PageForm(data=self.request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            try:
                page.put()
            except blog.SlugConstraintViolation:
                logging.error('Slug "%s" is not unique' % page.slug)
                self.render_form(page, form)
            else:
                self.redirect(page.get_absolute_url())
        else:
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
class PostForm(djangoforms.ModelForm):
    class Meta():
        model = blog.Post
        #_class is a property of polymodel used to track its
        #instances
        exclude = ['body_html', 'excerpt_html', '_class', 'author',
                   'pub_date', 'updated']


class CreatePostHandler(webapp.RequestHandler):
    def get(self):
        page = view.Page()
        template_values = {
            'postform': PostForm()
            }
        page.render(self, 'templates/admin/post_form.html',
                    template_values)

    def post(self):
        new_post = blog.Post()
        new_post.title = self.request.get('title')
        new_post.body = self.request.get('body')

        slug = self.request.get('slug').strip()
        if slug == '':
            slug = blog.slugify(new_post.title)
        else:
            slug = blog.slugify(slug)
        new_post.slug = slug

        excerpt = self.request.get('excerpt').strip()
        if excerpt == '':
            excerpt = None
        new_post.excerpt = excerpt

        new_post.tags = self.request.get('tags').split()

        new_post.update_markdown_fields()

        if self.request.get('submit') == 'Submit':
            try:
                new_post.put()
            except blog.SlugConstraintViolation, e:
                template_values = {
                    'error_message': "".join(e.args),
                }
                page = view.Page()
                page.render(self, 'templates/error/error.html',
                            template_values)
                return

            helpers.ping_services()
            self.redirect(new_post.get_absolute_url())
        else:
            template_values = {
                'postform': PostForm(instance=new_post),
                'post': new_post,
            }
            page = view.Page()
            page.render(self, 'templates/admin/post_form.html',
                        template_values)


class DeletePostHandler(webapp.RequestHandler):
    def get(self, year, month, day, slug):
        p = helpers.get_post(year, month, day, slug)
        if p is not None:
            p.delete()
        memcache.flush_all()
        self.redirect(config.url)


class EditPostHandler(webapp.RequestHandler):
    def get(self, year, month, day, slug):
        post = helpers.get_post(year, month, day, slug)
        page = view.Page()
        if post == None:
            page.render_error(self, 404)
        else:
            template_values = {
                'action': post.get_edit_url(),
                'postform': PostForm(instance=post),
                'post': post,
            }
            page.render(self, 'templates/admin/post_form.html',
                        template_values)

    def post(self, year, month, day, slug):
        post = helpers.get_post(year, month, day, slug)
        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            post.title = self.request.get('title')
            post.body = self.request.get('body')

            slug = self.request.get('slug').strip()
            if slug == '':
                slug = blog.slugify(post.title)
            else:
                slug = blog.slugify(slug)
            post.slug = slug

            excerpt = self.request.get('excerpt').strip()
            if excerpt == '':
                excerpt = None
            post.excerpt = excerpt

            post.tags = self.request.get('tags').split()

            if self.request.get('submit') == 'Submit':
                try:
                    post.put()
                except blog.SlugConstraintViolation, e:
                    template_values = {
                        'error_message': "".join(e.args),
                        }
                    page = view.Page()
                    page.render(self, 'templates/error/error.html',
                                template_values)
                    return

                self.redirect(post.get_absolute_url())
            else:
                template_values = {
                    'action': post.get_edit_url(),
                    'postform': PostForm(instance=post),
                    'post': post,
                }
                page = view.Page()
                page.render(self, 'templates/admin/post_form.html',
                            template_values)
#}}}

class ClearCacheHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/admin')

