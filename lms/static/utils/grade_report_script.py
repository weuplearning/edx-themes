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


import json
import time
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font


# from datetime import datetime, date, timedelta
# from django.utils import timezone
# from dateutil import tz


from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import logging
log = logging.getLogger()


emails = sys.argv[1].split(";")
course_ids = sys.argv[2].split(";")

all_users_data = {}


for course_id in course_ids:
  course_key = CourseLocator.from_string(course_id)
  course = get_course_by_id(course_key)
  course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
  course_name = course.display_name_with_default

  course_data = {}

  for i in range(len(course_enrollments)):
    user = course_enrollments[i].user
    user_data = {}

    enrollment = course_enrollments[i]
    if str(user.email).find('@yopmail') != -1 or str(user.email).find('@weuplearning') != -1 or str(user.email).find('@themoocagency') != -1 :
      continue

    try:
      user_data["id"] = user.id
    except:
      user_data["id"] = 'n.a.'

    try:
      user_data["email"] = user.email
    except:
      try:
        user_data["email"] = json.loads(user.profile.custom_field)['email']
      except:
        user_data["email"] = 'n.a.'
    
    user_data["name"] = user.profile.name

    try:
      user_data["Code"] = json.loads(user.profile.custom_field)['postal_code']
    except:
      user_data["Code"] = 'n.a.'

    # Grade
    gradesTest = check_best_grade(user, course, force_best_grade=True)
    # log.info(gradesTest.summary['percent'])
    # log.info(gradesTest.summary['section_breakdown'])
    userPersentGrade = gradesTest.summary['percent']

    try:
      user_data['grade'] = userPersentGrade * 100
    except:
      user_data['grade'] = 0


    data = { "general": user_data }
    course_data[str(user.id)]= data

  all_users_data[course_id]= course_data

# log.info('------------> Finish fetching user data and answers')
# log.info('------------> Begin Calculate grades and write xlsx report')

# WRITE XLS
timestr = time.strftime("%Y_%m_%d")
wb = Workbook()
sheet = wb.active
sheet.title= 'Rapport de notes'
filename = '/home/edxtma/csv/{}_grand-reims_grade_report.xlsx'.format(timestr)

headers = ['ID apprenant', 'Email', 'Nom d\'utilisateur' , 'Note finale', 'Code postal', 'Certificat']
for i, header in enumerate(headers):
  sheet.cell(1, i+1, header)
  sheet.cell(1, i+1).fill = PatternFill("solid", fgColor="59C4C6")
  sheet.cell(1, i+1).font = Font(b=False, color="FFFFFF")

j=2

for k, course_id in all_users_data.items():

  for key, user in course_id.items():

    sheet.cell(j, 1, user['general']['id'])
    sheet.cell(j, 2, user['general']['email'])
    sheet.cell(j, 3, user['general']['name'] )

    percent = str(user['general']['grade']) + '%'
    sheet.cell(j, 4, percent.replace('.',','))
    sheet.cell(j, 5, user['general']['Code'])

    if int(percent.split('.')[0]) >= 70 : 
      sheet.cell(j, 6, 'Oui')
      sheet.cell(j, 6).fill = PatternFill("solid", fgColor="21ad73")
      sheet.cell(j, 6).font = Font(b=False, color="FFFFFF")
    else:
      sheet.cell(j, 6, 'Non')
      sheet.cell(j, 6).fill = PatternFill("solid", fgColor="E24729")
      sheet.cell(j, 6).font = Font(b=False, color="FFFFFF")

    j += 1


# SEND MAILS
# course_names = []
course_names_html = []
for course_id in course_ids: 
  course = get_course_by_id(CourseLocator.from_string(course_id)) 
  # course_names.append(course.display_name_with_default)
  course_names_html.append("<li>"+ str(course.display_name_with_default)+"</li>")

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()
course_names_html = ''.join(course_names_html)

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note : "+ course_names_html +"<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"

for email in emails:

  part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
  fromaddr = "ne-pas-repondre@themoocagency.com"
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = email
  msg['Subject'] = "grand_reims_grade_report"
  attachment = _files_values
  part = MIMEBase('application', 'octet-stream')
  part.set_payload(attachment)
  encoders.encode_base64(part)
  part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(filename))
  msg.attach(part)
  server = smtplib.SMTP('mail3.themoocagency.com', 25)
  server.starttls()
  server.login('contact', 'waSwv6Eqer89')
  msg.attach(part2)
  text = msg.as_string()
  server.sendmail(fromaddr, email, text)
  server.quit()
  log.info('Email sent to '+str(email))


log.info('------------> Finish calculate grades and write xlsx report')


# Qualif
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/grand-reims/lms/static/utils/grade_report_script.py 'cyril.adolf@weuplearning.com' course-v1:grand-reims+01+2023


# Prod
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/grand-reims/lms/static/utils/grade_report_script.py 'cyril.adolf@weuplearning.com' course-v1:grand-reims+01+session01
