import import_wrapper
import datetime
import config
import logging

from smartypants import smartyPants
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.template import defaultfilters
from django.utils.translation import ngettext
from django.utils.simplejson import decoder


register = template.create_template_register()

@register.filter
def rfc3339(date):
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTF'

    def dst(self, dt):
        return datetime.timedelta(0)
utc = UTC()

def _jsontime_timezone(zone):
    """Fetches tzinfo objects from json-time service."""
    endpoint = 'http://json-time.appspot.com/time.json'
    tz = utc

    result = urlfetch.fetch('%s?tz=%s' % (endpoint, zone))

    if result.status_code != 200:
        logging.error('Service JsonTime returned unexpected status code: %d'
                      % result.status_code)
    else:
        try:
            json = decoder.JSONDecoder().decode(result.content)
        except ValueError:
            logging.error('Service JsonTime returned non-json content')
        else:
            if json['error']:
                logging.error('Invalid timezone "%s" in config.py. '
                              'Falling back to UTC.' % zone)
            else:
                logging.info(json['datetime'])
                date = parser.parse(json['datetime'])
                tz = date.tzinfo
    return tz

@register.filter
def tz_date(date, fmt="%F %d %Y %H:%M"):
    # without this, unpickling from memcache fails badly
    import_wrapper.load_zip('dateutil')
    from dateutil import parser
    tz = memcache.get('tz')
    if tz is None:
        zone = config.timezone
        if not zone:
            tz = utc
        else:
            tz = _jsontime_timezone(zone)
        memcache.set('tz', tz)
    return date.replace(tzinfo=utc).astimezone(tz).strftime(fmt)

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

    return ('%d %s ago') % (count, name(count))

@register.filter
def links_for_models(model_list, separator=None, use_ul=False):
    fmt = ('%(before)s<a href="%(link)s" '
           'title="%(title)s">%(title)s</a>%(after)s')
    if use_ul:
        values = dict(begin='<ul>', end='</ul>', before='<li>', after='</li>')
    else:
        values = dict(begin='', end='', before='', after='')
    if separator is None:
        separator = ''

    result = []
    for model in model_list:
        values['link'] = model.get_absolute_url()
        values['title'] = model.title
        result.append(fmt % values)
    values['result'] = separator.join(result)
    return '%(begin)s%(result)s%(end)s' % values

@register.filter
def ul_links_for_models(model_list, separator=None):
    return links_for_models(model_list, separator, True)

@register.filter
def smartypants(text):
    return smartyPants(text)

