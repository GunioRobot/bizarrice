import import_wrapper
import config
import logging
import xmlrpclib

from xmlrpc import GoogleXMLRPCTransport


def ping_services():
    logging.debug('Starting ping_services()')
    if not config.debug:
        if config.pingomatic:
            ping_service('http://rpc.pingomatic.com/', 'Ping-o-Matic')
        if config.feedburner:
            ping_service('http://ping.feedburner.com/', 'FeedBurner')

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

