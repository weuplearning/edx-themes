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

startup = importlib.import_module("lms.startup")
startup.run()

from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.courseware.courses import get_course_by_id
from student.models import CourseEnrollment
from student.models import User
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from openedx.core.djangoapps.site_configuration import helpers 
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade


from openpyxl import Workbook
import json


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


from datetime import timedelta
from django.utils import timezone


import logging
log = logging.getLogger()




emails_to_send = sys.argv[1].split(";")


all_treated_users = []
course_ids = [
    "course-v1:formation-securite-incendie+BI05+2024",
    "course-v1:formation-securite-incendie+BE53+2024",
    "course-v1:formation-securite-incendie+BE08+2024",
    "course-v1:formation-securite-incendie+BI28+2024",
    "course-v1:formation-securite-incendie+BI26+2024",
    "course-v1:formation-securite-incendie+BI50+2024",
    "course-v1:formation-securite-incendie+BE07+2024",
    "course-v1:formation-securite-incendie+BI48+2024",
    "course-v1:formation-securite-incendie+BI49+2024",
    "course-v1:formation-securite-incendie+BI46+2024",
    "course-v1:formation-securite-incendie+BI59+2024",
    "course-v1:formation-securite-incendie+BI47+2024",
    "course-v1:formation-securite-incendie+BI47UF+2024",
    "course-v1:formation-securite-incendie+BI60+2024",
    "course-v1:formation-securite-incendie+BE24+2024",
    "course-v1:formation-securite-incendie+BE25+2024",
    "course-v1:formation-securite-incendie+BI21+2024"
]



for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)
    batiment = course_id.split('+')[1]

    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        enrollment = course_enrollments[i]

        if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 :
           continue


        user_data = {}


        user_data.append(user.email) 
        user_data.append(user.username)
        user_data.append(json.loads(user.profile.custom_field).get('pro_serial_number','n.a.'))
        user_data.append(batiment)


        # date d'évaluation ? 

        gradesTest = check_best_grade(user, course, force_best_grade=True)
        log.info('gradesTest')
        log.info(gradesTest)
        log.info(dir(gradesTest))
        log.info(gradesTest.summary)



        all_treated_users.append(user_data)



## Workbook
wb = Workbook() 
sheet = wb.active

l=1
k=1
for user_data in all_treated_users:

    for data in user_data :
        sheet.cell(row=k, column=l).value = data
        l+=1

    k+=1


filename = "CHRU_Nancy_report.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note concernant les utilisateurs des différentes formations CHRU Nancy Sécurité Incendie<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport deleted users"

    attachment = _files_values
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= {}".format(filename))
    msg.attach(part)

    server = smtplib.SMTP('mail3.themoocagency.com', 25)
    server.starttls()
    server.login('contact', 'waSwv6Eqer89')
    msg.attach(part2)
    text = msg.as_string()
    server.sendmail(fromaddr, email, text)
    server.quit()

    print('Email sent to ',email)


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/formation-securite-incendie/lms/utils/all_courses_data_script.py 'cyril.adolf@weuplearning.com'
