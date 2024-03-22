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
import datetime

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font


# from datetime import datetime, date, timedelta
# from django.utils import timezone
# from dateutil import tz


from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade
from lms.djangoapps.wul_apps.models import WulCourseEnrollment


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

    # try:
    #   user_data["id"] = user.id
    # except:
    #   user_data["id"] = 'n.a.'

    try:
      user_data["email"] = user.email
    except:
      try:
        user_data["email"] = json.loads(user.profile.custom_field)['email']
      except:
        user_data["email"] = 'n.a.'
    
    # user_data["name"] = user.profile.name

    try:
      user_data["date_joined"] = user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    except:
      user_data["date_joined"] = 'n.a.'

    try:
      user_data["last_login"] = user.last_login.strftime('%Y-%m-%d %H:%M:%S')
    except:
      user_data["last_login"] = 'n.a.'

    try:
      user_data["first_name"] = json.loads(user.profile.custom_field)['first_name']
    except:
      user_data["first_name"] = 'n.a.'

    try:
      user_data["last_name"] = json.loads(user.profile.custom_field)['last_name']
    except:
      user_data["last_name"] = 'n.a.'

    try:
      user_data["structure"] = json.loads(user.profile.custom_field)['structure']
    except:
      user_data["structure"] = 'n.a.'

    try:
      user_data["preparedDiploma"] = json.loads(user.profile.custom_field)['preparedDiploma']
    except:
      user_data["preparedDiploma"] = 'n.a.'

    try:
      user_data["status"] = json.loads(user.profile.custom_field)['status']
    except:
      user_data["status"] = 'n.a.'

    try:
      user_data["regions"] = json.loads(user.profile.custom_field)['regions']
    except:
      user_data["regions"] = 'n.a.'


    #TimeTracking
    try:
      wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
      global_time_tracking = wul_course_enrollment.global_time_tracking
      # global_time_tracking_cumul += global_time_tracking
    except:
      global_time_tracking = 0
      

    user_data['timetracking'] = global_time_tracking

    user_data['timetracking'] = datetime.timedelta(seconds=global_time_tracking)






    # Grade
    grade_list = []

    gradesTest = check_best_grade(user, course, force_best_grade=True)

    for module in gradesTest.summary['section_breakdown'] :
      grade_list.append(module['percent'])

    userPersentGrade = gradesTest.summary['percent']
    grade_list.append(userPersentGrade)


    user_data['grade_list'] = grade_list 


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
filename = '/home/edxtma/csv/{}_umn_grade_report.xlsx'.format(timestr)

headers = ['Prénom', 'Nom', 'Email', "Date d'inscription", 'Dernière connexion', 'Structure', 'Diplôme préparé', 'Status', 'Région', 'Temps passé total', 'Note Module 1.1 ', 'Note Module 1.2', 'Note Module 1.3', 'Note Module 1.4', 'Note Module 1.5','Moyenne Module 1', 'Note Module 2.1', 'Note Module 2.2', 'Note Module 2.3', 'Note Module 2.4','Moyenne Module 2', 'Note Module 3.1', 'Note Module 3.2', 'Note Module 3.3', 'Note Module 3,4', 'Note Module 3,5', 'Note Module 3.6', 'Note Module 3.7', 'Moyenne Module 3', 'Note Module 4.1', 'Note Module 4.2', 'Moyenne Module 4', 'Note finale']
for i, header in enumerate(headers):
  sheet.cell(1, i+1, header)
  sheet.cell(1, i+1).fill = PatternFill("solid", fgColor="007DFF")
  sheet.cell(1, i+1).font = Font(b=False, color="FFFFFF")

j=2

for k, course_id in all_users_data.items():

  for key, user in course_id.items():

    sheet.cell(j, 1, user['general']['first_name'])
    sheet.cell(j, 2, user['general']['last_name'])
    sheet.cell(j, 3, user['general']['email'])
    sheet.cell(j, 4, user['general']['date_joined'])
    sheet.cell(j, 5, user['general']['last_login'])
    sheet.cell(j, 6, user['general']['structure'] )
    sheet.cell(j, 7, user['general']['preparedDiploma'] )
    sheet.cell(j, 8, user['general']['status'] )
    sheet.cell(j, 9, user['general']['regions'] )
    sheet.cell(j, 10, user['general']['timetracking'] )
    i=10

    save_grade = 0
    for grade in user['general']['grade_list'] :
      i += 1
      save_grade = grade

      percent = str(grade) + '%'
      sheet.cell(j, i, percent.replace('.',','))

    if int(save_grade) >= 70 : 
      sheet.cell(j, i).fill = PatternFill("solid", fgColor="21ad73")
      sheet.cell(j, i).font = Font(b=False, color="FFFFFF")
    else:
      sheet.cell(j, i).fill = PatternFill("solid", fgColor="ED4D39")
      sheet.cell(j, i).font = Font(b=False, color="FFFFFF")

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
  msg['Subject'] = "umn_grade_report"
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


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/grade_report_script.py 'cyril.adolf@weuplearning.com' course-v1:umn+test+test



