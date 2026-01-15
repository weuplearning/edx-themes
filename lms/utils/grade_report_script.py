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
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

from openpyxl import Workbook
import json
import datetime


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



import logging
log = logging.getLogger()


emails_to_send = sys.argv[1].split(";")

all_treated_users = []
headers = ["Email", "Pseudo", "Pays", "Ville", "Activité", "Activité - Si autre", "Année de naissance","Genre", "Date d'évaluation (YYYY-mm-dd)", "Durée (hh:mm:ss)", "Statut"]
all_treated_users.append(headers)

course_ids = [
    "course-v1:max-havelaar+01+01"
]



def get_best_grade_data(user, course_key, course_id, course_grade):

    try :
        wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
    except :
        wul_course_enrollment = False


    CF_data = json.loads(user.profile.custom_field)
    CF_field_to_check = 'success_date_' + str(course_id)

    if wul_course_enrollment and wul_course_enrollment.best_grade_date :
        best_grade_date = str(wul_course_enrollment.best_grade_date).split(' ')[0]
    elif CF_field_to_check in CF_data:
        best_grade_date = CF_data[CF_field_to_check]
    else:
        best_grade_date = 'n.a.'

    data = {
        'best_grade_date': best_grade_date,
        'global_time_tracking': wul_course_enrollment.global_time_tracking if wul_course_enrollment and wul_course_enrollment.global_time_tracking else 0,
        'status': 'Validé' if float(course_grade.percent) >= 0.8 else 'Non validé'
    }

    return data



for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)

    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        enrollment = course_enrollments[i]

        if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 :
           continue

        user_data = []
        log.info(user.email)


        user_data.append(user.email) 
        user_data.append(user.username)
   
        CF_data = json.loads(user.profile.custom_field)
        user_data.append(CF_data.get('country', 'n.a.')) 
        user_data.append(CF_data.get('city', 'n.a.')) 
        user_data.append(CF_data.get('activity', 'n.a.')) 
        user_data.append(CF_data.get('activity_other', 'n.a.')) 
        user_data.append(CF_data.get('birth_year', 'n.a.')) 
        user_data.append(CF_data.get('gender', 'n.a.')) 


        course_grade = CourseGradeFactory().update(user, course)
        data = get_best_grade_data(user, course_key, course_id, course_grade)

        user_data.append(data["best_grade_date"])
        user_data.append(datetime.timedelta(seconds=data["global_time_tracking"]))
        user_data.append(data["status"])

        all_treated_users.append(user_data)



## Workbook
wb = Workbook() 
sheet = wb.active


l=1
for user_data in all_treated_users:
    k=1
    for data in user_data :
        sheet.cell(row=l, column=k).value = data
        k+=1

    l+=1


filename = "maxhavelaar_report.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note concernant les utilisateurs inscrits au MOOC Max Havelaar<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport Max Havelaar"

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


# sudo /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/max-havelaar/lms/utils/grade_report_script.py 'cyril.adolf@weuplearning.com'



