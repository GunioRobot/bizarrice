import pytz
import config
import logging

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.template import defaultfilters


register = template.create_template_register()

def tz_date(date, fmt="%F %d %Y %H:%M"):
    tz = memcache.get('tz')
    if tz is None:
        zone = config.SETTINGS['timezone']
        if zone in pytz.all_timezones:
            tz = pytz.timezone(zone)
        elif not zone:
            tz = pytz.UTC
        else:
            logging.error('Invalid timezone "%s" in config.py. Falling '
                          'back to UTC.' % zone)
            tz = pytz.UTC
        memcache.set('tz', tz)
    return date.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)

register.filter(tz_date)
