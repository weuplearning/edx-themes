import importlib
import csv
import time
import os
import json
from datetime import datetime


from io import BytesIO


from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
from lms.djangoapps.wul_apps.models import WulCourseEnrollment


import logging
log = logging.getLogger()


courses_list = ['course-v1:deeptechforbusiness+FR+2021']

for course_id in courses_list:
    # Get enrollment
    log.info(course_id) 
    course_key = CourseKey.from_string(course_id)
    log.info(course_key)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)

    for enrollment in course_enrollments:

        string_data = str(enrollment)
        date_registration = datetime.strptime(string_data.split(' ')[3].replace('(',''), '%Y-%m-%d')
        log.info('date_registration :')
        log.info(date_registration)
        
        today =  datetime.now()
        time_delta = (today - date_registration).days
        log.info('time_delta')
        log.info(time_delta)

        if time_delta > 9 :
            log.info('HERE')
            log.info(enrollment.user)
            admin_list = ['fsegalen@netexplo.org', 'eruch-ext@netexplo.org']

            log.info(dir(enrollment.user))
            log.info('enrollment.user.is_staff')
            log.info(enrollment.user.is_staff)

            user = enrollment.user
            log.info(user.email)
            log.info(user.email.find("@themoocagency"))
            log.info(user.email.find("@weuplearning"))

            if user.email not in admin_list and user.email.find("@weuplearning")== -1 and user.email.find("@themoocagency")==-1 : 


                log.info('will be delete :')
                log.info(CourseEnrollment)
                log.info(dir(CourseEnrollment))
                # CourseEnrollment.unenroll_by_email(user.email, course_key)


# List of command to execute: 
# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/deeptechforbusiness/lms/utils/script_unenroll_users_koa.py