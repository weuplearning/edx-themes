import importlib
import csv
import time
import os
import json
from datetime import datetime


from io import BytesIO


from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey


import logging
log = logging.getLogger()


courses_list = ['course-v1:deeptechforbusiness+FR+2021', 'course-v1:deeptechforbusiness+EN+2021']

admin_list = ['fsegalen@netexplo.org', 'lnyadanu@netexplo.org', 'eruch-ext@netexplo.org', 'learning@netexplo.org']


for course_id in courses_list:

    course_key = CourseKey.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)

    for enrollment in course_enrollments:

        string_data = str(enrollment)
        date_registration = datetime.strptime(string_data.split(' ')[3].replace('(',''), '%Y-%m-%d')
        log.info('date_registration :')
        log.info(date_registration)
        
        today = datetime.now()
        time_delta = (today - date_registration).days
        log.info('time_delta')
        log.info(time_delta)

        if time_delta > 9 :

            user = enrollment.user

            if user.email not in admin_list and user.email.find("@weuplearning") == -1 and user.email.find("@themoocagency") == -1 : 

                log.info(course_key)
                log.info('will be delete :')
                log.info(user.email)
                CourseEnrollment.unenroll_by_email(user.email, course_key)


log.info('End')


# List of command to execute: 
# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/deeptechforbusiness/lms/utils/script_unenroll_users_koa.py
