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
                    u = User.objects.create_user(user.nickname(),
                                                 user.email())
                    if users.is_current_user_admin():
                        u.is_staff = True
                        u.is_superuser = True
                        u.save()
                    request._cached_user = u
            else:
                request._cached_user = AnonymousUser()
        return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUser()
        return None
