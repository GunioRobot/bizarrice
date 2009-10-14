#!/usr/bin/python2.5
# -*- coding: utf-8 -*-

import import_wrapper
from remote_console import read_options, setup, setup_gae


def save_backup(item, directory, has_tags=False):
    filename = 'backup/%s/%s-%s.md' % (directory,
                                       item.pub_date.strftime('%Y-%m-%d'),
                                       item.slug)
    fd = file(filename, 'w')
    fd.write('<!-- TITLE: %s -->\n' % item.title.encode('utf-8'))
    fd.write('<!-- PUB_DATE: %s -->\n' %
             item.pub_date.strftime('%Y,%m,%d,%H,%M,%S'))
    fd.write('<!-- UPDATED: %s -->\n' %
             item.updated.strftime('%Y,%m,%d,%H,%M,%S'))
    if has_tags:
        fd.write('<!-- TAGS: %s -->\n' % ' '.join(item.tags))
    fd.write('\n')
    fd.write(item.body.encode('utf-8'))

def backup_posts():
    from blog.models import Post

    posts = Post.all().fetch(1000)
    for post in posts:
        save_backup(post, 'posts', has_tags=True)

def backup_pages(count=False, offset=0):
    from blog.models import Page

    pages = Page.all().fetch(1000)
    for page in pages:
        save_backup(page, 'pages')

def main():
    setup_gae()
    options = read_options()
    setup(**options)
    backup_posts()
    backup_pages()

if __name__ == '__main__':
    main()
