import view
import helpers
import config

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from models import blog

class PostForm(djangoforms.ModelForm):
    class Meta:
        model = blog.Post
        #_class is a property of polymodel used to track its
        #instances
        exclude = ['body_html','excerpt_html','_class','author']
        

class AdminHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
            'posts': blog.Post.all().order('-pub_date'),
            'pages': blog.Page.all().order('index'),
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
            slug = blog.slugify(new_page.title)
        new_page.slug = slug
        index = self.request.get('index').strip()
        if index == '':
            index = 0
        new_page.index = int(index)

        new_page.put()
        if self.request.get('submit') == 'Submit':
            self.redirect(new_page.get_absolute_url())
        else:
            template_values = {
                'page': new_page,
                }
            page = view.Page()
            page.render(self, 'templates/admin/page_form.html',
                        template_values)


class DeletePageHandler(webapp.RequestHandler):
    def get(self, slug):
        p = helpers.get_page(slug)
        if p is not None:
            p.delete()
        memcache.flush_all()
        self.redirect(config.url)


class EditPageHandler(webapp.RequestHandler):
    def get(self, slug):
        p = helpers.get_page(slug)
        page = view.Page()
        if p is None:
            page.render_error(self, 404)
        else:
            template_values = {
                'action': p.get_edit_url(),
                'page': p,
            }
            page.render(self, 'templates/admin/page_form.html',
                        template_values)

    def post(self, slug):
        p = helpers.get_page(slug)
        page = view.Page()
        if p == None:
            page.render_error(self, 404)
        else:
            p.title = self.request.get('title')
            p.body = self.request.get('body')
            slug = self.request.get('slug').strip()
            if slug == '':
                slug = blog.slugify(p.title)
            p.slug = slug
            p.index = int(self.request.get('index', 0))

            p.put()
            if self.request.get('submit') == 'Submit':
                self.redirect(p.get_absolute_url())
            else:
                template_values = {
                    'action': p.get_edit_url(),
                    'page': p,
                }
                page = view.Page()
                page.render(self, 'templates/admin/page_form.html',
                            template_values)


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


class ClearCacheHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/admin')

