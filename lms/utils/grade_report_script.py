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
course_ids = sys.argv[2].split(";")

all_treated_users = []
headers = ["Email", "Nom", "Prénom", "Complétion - Gestion de son activité", "Complétion - Techniques commerciales", "Complétion - Prospection", "Complétion - Relation vendeurs", "Complétion - Relation acquéreurs", "Complétion - Négociation et conclusion", "Durée (hh:mm:ss)", "Statut"]

all_treated_users.append(headers)


for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)

    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        enrollment = course_enrollments[i]

        if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 or user.email.find('@yopmail') != -1 :
           continue

        user_data = []
        scorm_completion = []
        status = 'Validé'

        user_data.append(user.email) 
        user_data.append(json.loads(user.profile.custom_field).get('last_name','n.a.'))
        user_data.append(json.loads(user.profile.custom_field).get('first_name','n.a.'))

        try:
            wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
            global_time_tracking = wul_course_enrollment.global_time_tracking            
        except:
            global_time_tracking = 0


        # Course specific completion
        scorm_completion.append(json.loads(user.profile.custom_field).get('dbab78a6afa04e0bab328fcf2af89a8b','0%'))
        scorm_completion.append(json.loads(user.profile.custom_field).get('e9aa55435d8a4c4db87ef52e71c07cf6','0%'))
        scorm_completion.append(json.loads(user.profile.custom_field).get('269a0820af6d45b2b0e9d60dd9c877b9','0%'))
        scorm_completion.append(json.loads(user.profile.custom_field).get('9a82424a0aad44ca98f14f2cf974abaa','0%'))
        scorm_completion.append(json.loads(user.profile.custom_field).get('0c58d3450a0048558203b94f82620708','0%'))
        scorm_completion.append(json.loads(user.profile.custom_field).get('07ffd5c762294e94ae450cc932a23ebd','0%'))

        for i in range(len(scorm_completion)):
            value = scorm_completion[i].split(' ')[0]
            user_data.append(value)

            if int(value.split('%')[0]) <= 80:
                status = 'Non validé'

        user_data.append(datetime.timedelta(seconds=global_time_tracking))
        user_data.append(status)

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


filename = "grade_report_casavo.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note concernant les utilisateurs de la formation Casavo<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport Casavo"

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



# sudo /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/casavo/lms/utils/grade_report_script.py 'cyril.adolf@weuplearning.com;melanie.zunino@weuplearning.com' 'course-v1:casavo+01+FR'
