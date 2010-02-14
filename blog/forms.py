import blog
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms


class PageForm(djangoforms.ModelForm):
    class Meta():
        model = blog.Page
        exclude = ['body_html', '_class', 'author', 'pub_date', 'updated']


class LinkForm(djangoforms.ModelForm):
    class Meta():
        model = blog.Link
        exclude = ['body_html', '_class', 'author', 'pub_date', 'updated']


class PostForm(djangoforms.ModelForm):
    tags = djangoforms.forms.CharField(required=False)
    class Meta():
        model = blog.Post
        exclude = ['body_html', '_class', 'author', 'pub_date', 'updated',
                   'excerpt_html']

