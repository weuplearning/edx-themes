# -*- coding: utf-8 -*-
#!/usr/bin/env python
import importlib
import sys
importlib.reload(sys)
import os
from io import BytesIO
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.production")
os.environ.setdefault("LMS_CFG", "/edx/etc/lms.yml")
os.environ.setdefault("lms.envs.production,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#############################################################
#         ^ SETUP ENVIRONNEMENT VARIABLE FOR KOA ^          #
#                START BEYOND THIS LINE                     #
#############################################################



from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from datetime import datetime, date, timedelta


import logging
log = logging.getLogger()


courses_list = sys.argv[1].split(";")
days_limit = sys.argv[2]


admin_list = ['horen.lestang.isabelle@gmail.com','m.ashraf@outlook.fr', 'andrew.funck@hec.edu','schulte@hec.fr']



for course_id in courses_list:

    course_key = CourseKey.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)

    for enrollment in course_enrollments:

        string_data = str(enrollment)
        date_registration = datetime.strptime(string_data.split(' ')[3].replace('(',''), '%Y-%m-%d')
        
        today = datetime.now()
        time_delta = (today - date_registration).days

        if time_delta > int(days_limit) :

            user = enrollment.user

            if user.email not in admin_list and user.email.find("@weuplearning") == -1 : 

                CourseEnrollment.unenroll_by_email(user.email, course_key)
                log.info(str(user.username) + ' has been deleted from : ' + str(course_key))



# Run script
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/script_unenroll_users_koa.py 'course-v1:hec-pole-emploi+IP+2023;course-v1:hec-pole-emploi+IP_NEG+2023;course-v1:hec-pole-emploi+webinaire+2023;course-v1:hec-pole-emploi+NEG+2023' 30


