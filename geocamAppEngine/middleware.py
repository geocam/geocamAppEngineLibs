# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# [Modified to work with pure Django, 2012]

from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from google.appengine.api import users


class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            user = users.get_current_user()
            if user:
                try:
                    request._cached_user = User.objects.get(email=user.email())
                except ObjectDoesNotExist:
                    if users.is_current_user_admin():
                        # bootstrap -- treat any app engine admin user as a django superuser
                        u = User.objects.create_superuser(user.nickname(),
                                                          user.email())
                        request._cached_user = u
                    else:
                        # user logged in through app engine but not somebody we know
                        request._cached_user = AnonymousUser()
            else:
                request._cached_user = AnonymousUser()
        return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUser()
        return None