import config
import logging
import xmlrpclib
import xmlrpc

from xmlrpc import GoogleXMLRPCTransport
from urllib import urlencode
from urlparse import urljoin
from google.appengine.api import urlfetch


def ping_services():
    logging.debug('Starting ping_services()')
    if not config.debug:
        if config.pingomatic:
            ping_xmlrpc_service('http://rpc.pingomatic.com/',
                                name='Ping-o-Matic')
        if config.feedburner:
            ping_xmlrpc_service('http://ping.feedburner.com/',
                                name='FeedBurner')
        # PubSubHubbub
        ping_http_service('http://pubsubhubbub.appspot.com/',
                          {'hub.url': '%s/feed' % config.url,
                           'hub.mode': 'publish'},
                          name='PubSubHubbub')
        # Sitemaps ping
        ping_http_service('http://www.google.com/webmasters/tools/ping',
                          {'sitemap': '%s/sitemap.xml' % config.url},
                          name='Sitemaps',
                          mode=urlfetch.GET)
        # Blogsearch
        ping_http_service('http://blogsearch.google.com/ping',
                          {'url': '%s/feed' % config.url},
                          name='Google BlogSearch')

def ping_xmlrpc_service(endpoint, name=None):
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

def ping_http_service(url, params, name=None, mode=urlfetch.POST):
    if name is None:
        name = url
    logging.debug('Pinging %s' % name)

    data = urlencode(params)
    if mode == urlfetch.GET:
        url = '%s?%s' % (url, data)
    result = urlfetch.fetch(url, data, mode)

    if result.status_code / 100 != 2:
        logging.error('%d Error pinging %s' % (result.status_code, name))
    else:
        logging.debug('%s ping OK: %s' % (name, result.content))

