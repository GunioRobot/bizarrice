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

def backup_posts(count=False, offset=0):
    from models.blog import Post

    if not count:
        count = 1000
    else:
        count = Post.all().count()
        while count > 1000:
            backup_posts(1000, offset)
            count -= 1000
            offset += 1000

    if count == 0:
        return

    posts = Post.all().fetch(count, offset=offset)
    for post in posts:
        save_backup(post, 'posts', has_tags=True)

def backup_pages(count=False, offset=0):
    from models.blog import Page

    if not count:
        count = 1000
    else:
        count = Page.all().count()
        while count > 1000:
            backup_pages(1000, offset)
            count -= 1000
            offset += 1000

    if count == 0:
        return
    pages = Page.all().fetch(count, offset=offset)
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
