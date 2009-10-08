import datetime
import pytz
import config
import logging

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.template import defaultfilters
from django.utils.translation import ngettext


register = template.create_template_register()

@register.filter
def rfc3339(date):
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")

@register.filter
def tz_date(date, fmt="%F %d %Y %H:%M"):
    tz = memcache.get('tz')
    if tz is None:
        zone = config.timezone
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

@register.filter
def date_diff(d):
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    delta = now - d
    delta_midnight = today - d
    days = delta.days
    hours = round(delta.seconds / 3600., 0)
    minutes = round(delta.seconds / 60., 0)
    chunks = (
        (365.0, lambda n: ngettext('year', 'years', n)),
        (30.0, lambda n: ngettext('month', 'months', n)),
        (7.0, lambda n : ngettext('week', 'weeks', n)),
        (1.0, lambda n : ngettext('day', 'days', n)),
    )

    if days == 0:
        if hours == 0:
            if minutes > 0:
                return ngettext('1 minute ago', \
                                '%(minutes)d minutes ago', minutes) % \
                        {'minutes': minutes}
            else:
                return ("less than 1 minute ago")
        else:
            return ngettext('1 hour ago', '%(hours)d hours ago', hours) \
                    % {'hours':hours}

    if delta_midnight.days == 0:
        return ("yesterday at %s") % d.strftime("%H:%M")

    count = 0
    for i, (chunk, name) in enumerate(chunks):
        if days >= chunk:
            count = round((delta_midnight.days + 1)/chunk, 0)
            break

    return ('%(number)d %(type)s ago') % \
            {'number': count, 'type': name(count)}
