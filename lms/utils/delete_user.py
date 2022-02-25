# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import logging
import importlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.aws")
os.environ.setdefault("lms.envs.aws,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")

os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")

startup = importlib.import_module("lms.startup")
startup.run()

from django.http import HttpResponseRedirect, JsonResponse
from common.djangoapps.student.models import CourseEnrollment, User
from opaque_keys.edx.locations import SlashSeparatedCourseKey

log = logging.getLogger()

# users_list_to_delete = [
    
# ]

users_list_to_delete = User.objects.filter(email__endswith="yopmail.com")

log.info(users_list_to_delete)
for username in users_list_to_delete:
    user = User.objects.get(username=username)
    enrollments = CourseEnrollment.objects.filter(user=user)
    user_email = user.email

    for enrollment in enrollments :
        course_id = enrollment.course_id
        if "e-ferro" in str(course_id):
            log.info(username)
            log.info('[WUL] : {} has been unenrolled from : {}'.format(user_email, course_id))
            CourseEnrollment.unenroll(user, course_id)
    
    # if (len(enrollments) == 0) :
    #     user_id = user.id
    #     User.objects.get(id=user_id).delete()
    #     log.info('[WUL] : Successfully deleted user : {}'.format(user_email))
    # else:
    #     log.error('[WUL] : NOT ALL ENROLLMENTS DELETED FOR USER {}'.format(user_email))

# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/e-ferro/lms/utils/delete_user.py