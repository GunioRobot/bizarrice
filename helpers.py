import os
import string
import datetime
import config
import logging
import xmlrpclib
import blog

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from dateutil.relativedelta import *
from xmlrpc import GoogleXMLRPCTransport


def ping_services():
    logging.debug('Starting ping_services()')
    if not config.debug:
        if config.pingomatic:
            ping_service('http://rpc.pingomatic.com/', 'Ping-o-Matic')
        if config.feedburner:
            ping_feedburner('http://ping.feedburner.com/', 'FeedBurner')

def ping_service(endpoint, name=None):
    if name is None:
        name = endpoint
    logging.debug('Pinging %s' % name)

    rpc_server = xmlrpclib.ServerProxy(endpoint, GoogleXMLRPCTransport())
    feed_url = '%s/feed' % config.url
    response = rpc_server.weblogUpdates.ping(config.title, config.url,
                                             feed_url)

    msg = response.get('message', '(No message on RPC result)')
    if response.get('flerror'):
        logging.error('Ping error from %s: %s' % (name, msg))
    else:
        logging.debug('%s ping OK: %s' % (name, msg))

def get_post(year, month, day, slug):
    post = memcache.get('post-%s' % slug)
    if post is None:
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
        memcache.set('post-%s' % slug, post)
    return post

def get_page(slug):
    page = memcache.get('page-%s' % slug)
    if page is None:
        query = blog.Page.all()
        query.filter('slug = ', slug)
        page = query.get()
        memcache.set('page-%s' % slug, page)
    return page

def get_archive_list():
    """Return a list of the archive months and their article counts."""
    # Attempt to get a memcache'd copy first
    archive = memcache.get('archive_list')
    if archive is not None:
        return archive

    # Get the date of the oldest post
    query = db.Query(blog.Post)
    query.order('pub_date')
    oldest = query.get()

    # Handle the situation where there are no posts
    if oldest is None:
        memcache.set('archive_list', [])
        return []

    # Create a date delta for moving ahead 1 month
    plus_one_month = relativedelta(months=+1)

    # Calculate the start and end dates for the archive
    start_date = datetime.date(oldest.pub_date.year, oldest.pub_date.month, 1)
    end_date = datetime.date.today()
    end_date = datetime.date(end_date.year, end_date.month, 1) + plus_one_month

    # Loop through each month in the time span and count the number
    # of posts made in that month
    archive = []
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + plus_one_month

        query = db.Query(blog.Post)
        query.filter('pub_date >= ', current_date)
        query.filter('pub_date < ', next_date)

        archive.append({
            'date': current_date,
            'count': query.count(1000),
            'url': '/%04d/%02d' % (current_date.year, current_date.month),
        })
        current_date = next_date

    memcache.set('archive_list', archive)
    return archive

def get_tag_list():
    """Return a list of the tags and their article counts"""
    # Attempt to get a memcache'd copy first
    tag_list = memcache.get('tag_list')
    if tag_list is not None:
        return tag_list

    # Build a list of tags and their article counts
    tag_list = {}
    query = blog.Post.all()
    for post in query:
        for tag in post.tags:
            if tag in tag_list:
                tag_list[tag] += 1
            else:
                tag_list[tag] = 1

    # Sort the tag dictionary by name into a list
    # and add each tag's URL
    sorted_tag_list = []
    for tag in sorted(tag_list.iterkeys()):
        sorted_tag_list.append({
            'tag': tag,
            'count': tag_list[tag],
            'url': '/tag/%s' % (tag),
        })

    memcache.set('tag_list', sorted_tag_list)
    return sorted_tag_list

def get_page_list():
    pages = memcache.get('page_list')
    if pages is not None:
        return pages

    page_list = []
    page_list = blog.Page.all().order('index').fetch(1000)
    memcache.set('page_list', page_list)
    return page_list
