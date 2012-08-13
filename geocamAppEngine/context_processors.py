# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from google.appengine.api import users

from django.conf import settings


def AuthUrlsContextProcessor(request):
    """
    Adds login and logout urls to the context. This context processor works for app engine.
    A similar one for native Django is defined in:
      geocamUtil.context_processors.AuthUrlContextProcessor.AuthUrlContextProcessor
    """
    full_path = request.get_full_path()

    return {
        'login_url': users.create_login_url(full_path),
        'logout_url': users.create_logout_url(full_path),
        'login_url_with_next': users.create_login_url(getattr(settings, 'LOGIN_REDIRECT_URL',
                                                              full_path))
    }
