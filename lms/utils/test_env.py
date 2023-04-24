# -*- coding: utf-8 -*-
#!/usr/bin/env python
import importlib
import codecs
import sys
importlib.reload(sys)
import os
import yaml
from django.core.exceptions import ImproperlyConfigured
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.production")
os.environ.setdefault("LMS_CFG", "/edx/etc/lms.yml")
os.environ.setdefault("lms.envs.production,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = u"Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)
    
CONFIG_FILE = get_env_setting('LMS_CFG')

with codecs.open(CONFIG_FILE, encoding='utf-8') as f:
    __config__ = yaml.safe_load(f)
    ENV_TOKENS = __config__

    EMAIL_HOST_USER = ENV_TOKENS.get('EMAIL_HOST_USER', None)
    EMAIL_HOST_PASSWORD = ENV_TOKENS.get('EMAIL_HOST_PASSWORD', None)
    print(EMAIL_HOST_USER)
    print(EMAIL_HOST_PASSWORD)

# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/loveboating/lms/utils/test_env.py