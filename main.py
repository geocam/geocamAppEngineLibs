# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""
This is the equivalent of <site>/djangoWsgi.py but for use under Google App Engine.
"""

import os
import sys

import django
from django.core.handlers import wsgi
from django.core import management

from google.appengine.ext.webapp import util

_up = os.path.dirname
thisDir = _up(_up(_up(os.path.realpath(__file__))))
settings_path = 'settings'
os.environ['DJANGO_SETTINGS_MODULE'] = settings_path
os.environ['DJANGO_SCRIPT_NAME'] = '/'
sys.path.insert(0, os.path.join(thisDir, 'apps'))
sys.path.insert(0, os.path.join(thisDir, 'submodules', 'geocamAppEngineLibs'))

try:
    settings = __import__('settings')
    management.setup_environ(settings, original_settings_path=settings_path)
except ImportError:
    pass

app = wsgi.WSGIHandler()

def main():
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
