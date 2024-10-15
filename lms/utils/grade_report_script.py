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
    # if str(user.email).find('@yopmail') != -1 or str(user.email).find('@weuplearning') != -1 or str(user.email).find('@themoocagency') != -1 :
    #   continue
    try:
      user_data["email"] = user.email
    except:
      try:
        user_data["email"] = json.loads(user.profile.custom_field)['email']
      except:
        user_data["email"] = 'n.a.'
    
    user_data["name"] = user.profile.name

    try:
      user_data["adress"] = json.loads(user.profile.custom_field)['adress']
    except:
      user_data["adress"] = 'n.a.'

    try:
      user_data["post_code"] = json.loads(user.profile.custom_field)['post_code']
    except:
      user_data["post_code"] = 'n.a.'

    try:
      user_data["city"] = json.loads(user.profile.custom_field)['city']
    except:
      user_data["city"] = 'n.a.'

    try:
      user_data["region"] = json.loads(user.profile.custom_field)['region']
    except:
      user_data["region"] = 'n.a.'


    try:
      user_data["department"] = json.loads(user.profile.custom_field)['department']
    except:
      user_data["department"] = 'n.a.'

    try:
      user_data["parcours"] = json.loads(user.profile.custom_field)['parcours']
    except:
      user_data["parcours"] = 'n.a.'

    try:
      user_data["profession"] = json.loads(user.profile.custom_field)['profession']
    except:
      user_data["profession"] = 'n.a.'

    try:
      user_data["profession_autre"] = json.loads(user.profile.custom_field)['profession_autre']
    except:
      user_data["profession_autre"] = 'n.a.'

    try:
      user_data["icope_emailing"] = json.loads(user.profile.custom_field)['icope_emailing']
    except:
      user_data["icope_emailing"] = 'n.a.'





    log.info("user_data")
    log.info(user_data)

    user_grade = {}
    # Grade
    gradesTest = check_best_grade(user, course, force_best_grade=True)
    # log.info(gradesTest.summary['percent'])
    log.info('detailled grade')
    log.info(gradesTest.summary['section_breakdown'])


    userPersentGrade = gradesTest.summary['percent']
    user_grade['detailled'] = gradesTest.summary['section_breakdown']
    try:
      user_grade['global'] = userPersentGrade * 100
    except:
      user_grade['global'] = 0


    data = { "profil": user_data, "grades": user_grade }
    course_data[str(user.id)]= data

  all_users_data[course_id]= course_data

# log.info('------------> Finish fetching user data and answers')
# log.info('------------> Begin Calculate grades and write xlsx report')


# Différencier un rapport global et un rapport par région (se baser sur les CF ?) 


# WRITE XLS
timestr = time.strftime("%Y_%m_%d")
wb = Workbook()
sheet = wb.active
sheet.title= 'Rapport de notes'
filename = '/home/edxtma/csv/{}_icope_grade_report.xlsx'.format(timestr)

headers = ['Email', 'Nom d\'utilisateur', 'Adresse', 'Code postal', 'Ville',  'Région', 'Département', 'Parcours', 'Profession', 'Profession si autre', 'Newsletter','Note detaillée à compléter', 'Note finale']
for i, header in enumerate(headers):
  sheet.cell(1, i+1, header)
  sheet.cell(1, i+1).fill = PatternFill("solid", fgColor="59C4C6")
  sheet.cell(1, i+1).font = Font(b=False, color="FFFFFF")

j=2

for k, course_id in all_users_data.items():

  for key, user in course_id.items():

    i=0
    for key, value in  user['profil'].items() : 
      sheet.cell(j, i+1, value)
      i+=1


    for grade in user['grades']['detailled'] : 
      log.info("grade")
      log.info(grade)

      percent = str(grade["percent"]*100) + '%'
      sheet.cell(j, i+1, percent)
      i+=1

    percent_global = str(user['grades']['global']*100) + '%'
    sheet.cell(j, i+1, percent_global)


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
  msg['Subject'] = "icope_grade_report"
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
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/icope/lms/utils/grade_report_script.py 'cyril.adolf@weuplearning.com' course-v1:icope+1+2022



# Prod
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/icope/lms/utils/grade_report_script.py 'cyril.adolf@weuplearning.com' course-v1:icope+Nouvelle_Aquitaine+2022


