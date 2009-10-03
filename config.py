# -*- coding: utf-8 -*-
import os


APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SETTINGS = {
    'title': 'Caio Romão\'s Blog',
    'description': 'No proper description set',
    'author': 'Caio Romão',
    'email': 'caioromao@gmail.com',
    'url': 'http://blog.caioromao.com',
    'items_per_page': 10,
    # Enable/disable Google Analytics
    # Set to your tracking code (UA-xxxxxx-x), or False to disable
    'google_analytics': 'UA-4613689-4',
    # Enable/disable Disqus-based commenting for posts
    # Set to your Disqus short name, or False to disable
    'disqus': 'caio',
    # Enable/disable debug mode
    'debug': True,
}
