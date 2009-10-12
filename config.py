# -*- coding: utf-8 -*-
import os


APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

title = 'Blog Title'
description = 'Description'
author = 'Author'
email = 'Email'
url = 'BlogURL'
items_per_page = 10
# The Blog theme. It should be the name of the directory under 'themes/'
# if set to False or an invalid theme, it will fall back to default.
theme = 'default'
# Enable/disable Google Analytics
# Set to your tracking code (UA-xxxxxx-x), or False to disable
google_analytics = False
# Enable/disable Disqus-based commenting for posts
# Set to your Disqus short name, or False to disable
disqus = False
# Enable/disable debug mode
debug = True
# Set your Timezone. Set False to use the default (UTC)
# http://en.wikipedia.org/wiki/List_of_zoneinfo_timezones (TZ column)
timezone = False
# Enable/Disable using feedburner to publish feeds
# Set to your Feedburner shortname, or False to disable
feedburner = False
# Enable/Disable pinging ping-o-matic after publishing a post.
# Accepted values: True or False.
pingomatic = False

try:
    from local_config import *
except ImportError:
    pass
