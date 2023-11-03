from django.contrib.auth import get_user_model
import openedx.core.djangoapps.user_authn.migrations

import importlib
import sys
importlib.reload(sys)
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.production")
os.environ.setdefault("LMS_CFG", "/edx/etc/lms.yml")
os.environ.setdefault("lms.envs.production,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#emailproviders = ['@gmail.com', '@hotmail.com','@hotmail.fr','@icloud.com','@yahoo.fr','@outlook.fr']
users = get_user_model().objects.exclude(email__endswith='@weuplearning.com').exclude(email__endswith='@themoocagency.com').exclude(email__endswith='@example.com').exclude(email__endswith='@fake.email')# | get_user_model().objects.exclude(email__endswith='@themoocagency.com').values()# | @example.com
#try:
#    alexb = users.get(email='alexandre.berteau@themoocagency.com')
#    annojan = users.get(email='annojan.kandiah@weuplearning.com')
#    print(alexb)
#    print(annojan)
#except:
#    print("error")

#for emailprovider in emailproviders:
#    users = get_user_model().objects.filter(email__iendswith=emailprovider)
#    print(users)
i=0
for user in users:
    print(user)
    user.delete()

print(len(users))

# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/amazon-belgique/lms/utils/delete_users.py
