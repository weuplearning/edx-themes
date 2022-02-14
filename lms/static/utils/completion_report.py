
import os
from io import BytesIO
import json
import time

from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from courseware.courses import get_course_by_id
from lms.djangoapps.grades.context import grading_context_for_course
from lms.djangoapps.courseware.user_state_client import DjangoXBlockUserStateClient

from openpyxl import Workbook

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from datetime import datetime, date, timedelta
from django.utils import timezone

import logging
log = logging.getLogger()


# Can not manage to pass var as arguments in command line
course_ids = ['course-v1:bmd+testconditional+2021']
# course_ids = ['course-v1:bmd+FR+2022_02_9-10']
emails =['cyril.adolf@weuplearning.com']


all_users_data = {}
log.info('------------> Begin fetching user data and answers')

at_least_one_student = False

for course_id in course_ids:
  course_key = CourseLocator.from_string(course_id)
  course = get_course_by_id(course_key)
  course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
  course_name = course.display_name_with_default

  course_data = {}

  log.info(course_id)

  # session
  session = course_id.split('+')[1]
  log.info('-----> session: '+ str(session))

  for i in range(len(course_enrollments)):
    user = course_enrollments[i].user
    log.info(user)
    user_data = {}        


    # if str(user.email).find('@yopmail') != -1 or str(user.email).find('@weuplearning') != -1 or str(user.email).find('@themoocagency') != -1 :
    #   log.info('Yopmail account ' + str(user))
    #   continue

    # Update object with user data without grades

    
    at_least_one_student = True
    user_data["session"] = session

    try:
      user_data["email"] = user.email
    except:
      try:
        user_data["email"] = json.loads(user.profile.custom_field)['email']
      except:
        user_data["email"] = 'n.a.'

    try:
      user_data["firstname"] = user.first_name.capitalize()
    except:
      try:
        user_data["firstname"] = json.loads(user.profile.custom_field)['first_name'].capitalize()
      except:
        user_data["firstname"] = 'n.a.'

    try:
      user_data["lastname"] = user.last_name.capitalize()
    except:
      try:
        user_data["lastname"] = json.loads(user.profile.custom_field)['last_name'].capitalize()
      except:
        user_data["lastname"] = 'n.a.'

    # Access Section
    scorable_block_titles = []
    grading_context = grading_context_for_course(course)
    user_state_client = DjangoXBlockUserStateClient()
    list_question = []

    log.info('grading_context')
    log.info(grading_context['all_graded_subsections_by_type']['Knowledge Test'])

    for section in grading_context['all_graded_subsections_by_type']['Knowledge Test']:
        for unit in section['scored_descendants']:
            log.info('unit')
            log.info(unit)
            scorable_block_titles.append((unit.location))

    for block_location in scorable_block_titles:

      question = {}
      try:
        history_entries = list(user_state_client.get_history(user.username, block_location))
      except: 
        question['choice'] = 'n.a.'
        question['correctedGrade'] = 0
        question['time'] = 'n.a.'
        question['score'] = 'n.a.'
        continue

      problemNum = str(block_location)[-2:]
      question['problem'] = problemNum
      choices = []
      

      log.info('history_entries[0].state')
      log.info(history_entries[0].state)
      log.info(history_entries[0])
      log.info(dir(history_entries[0]))
      log.info("----------------------")


      if len(history_entries[0].state) ==3:
        question['choice'] = 'n.a.'
      else:
        for key, value in history_entries[0].state['student_answers'].items():
          choices = value
          question['choice'] = value

      question['correctedGrade'] = 0

      try:
        question['time'] = history_entries[0].state['last_submission_time']
      except:
        question['time'] = 'n.a.'

      try:
        question['score'] = history_entries[0].state['score']['raw_earned']
      except:
        question['score'] = 'n.a.'

      list_question.append(question)

    data = { "general": user_data, 'list_question' : list_question }
    course_data[str(user.id)]= data
  all_users_data[course_id]= course_data

log.info('------------> Finish fetching user data and answers')

log.info('------------> Begin Calculate grades and write xlsx report')
# Grades need to be recalculate :
# We need to generate un json when the course is converted. 
# Then we can fetch it using the course name (value given when creating the tar.gz) 

course_names = []
course_names_html = []
for course_id in course_ids: 
    course = get_course_by_id(CourseLocator.from_string(course_id)) 
    course_names.append(course.display_name_with_default)
    course_names_html.append("<li>"+ str(course.display_name_with_default)+"</li>")
    # course_names_html.append("<li>"+ str(course.display_name_with_default.encode('ascii', errors='xmlcharrefreplace'))+"</li>")

# WRITE XLS
timestr = time.strftime("%Y_%m_%d")
wb = Workbook()
sheet = wb.active
sheet.title= 'Rapport'
filename = '/home/edxtma/csv/{}_BMD_grade_report.xls'.format(timestr)

headers = ['Adresse e-mail', 'Prénom', 'Nom', 'Session', 'Score' ,'Validation']
first = True

for i, header in enumerate(headers):
  sheet.cell(1, i+1, header)
j=2
for k, course_id in all_users_data.items():
  for key, user in course_id.items():
    sheet.cell(j, 1, user['general']['email'])
    sheet.cell(j, 2, user['general']['firstname'])
    sheet.cell(j, 3, user['general']['lastname'])
    # Session
    sheet.cell(j, 4, user['general']['session'])

    correctedExamGrade = 0
    i = 5 
    for question in user['list_question']:
      # correctedGrade = 0

      # if first:  
      #   sheet.cell(1, i+1, question['problem'])
      #   sheet.cell(1, i+2, 'Score')
      #   sheet.cell(1, i+3, 'Réponses choisies')
      # sheet.cell(j, i+1, question['time'])

      correctedGrade = question['correctedGrade']
      choices = ''
      for choice in question['choice'] :
        choices += str(choice) + ' '

      # sheet.cell(j, i+2, correctedGrade)
      # sheet.cell(j, i+3, choices)

      correctedExamGrade += int(correctedGrade)
      # i += 3
    sheet.cell(j, i, correctedExamGrade)
    if correctedExamGrade >= 21: 
      sheet.cell(j, i+1, 'oui')
    else :
      sheet.cell(j, i+1, 'non')

    # first = False
    j += 1
sheet.cell(1, i+1, 'Note finale')


# SEND MAILS
output = BytesIO()
wb.save(output)
_files_values = output.getvalue()
course_names_html = ''.join(course_names_html)

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note : "+ course_names_html +"<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"

for email in emails:
  if not at_least_one_student :
    log.info('at_least_one_student')
    log.info(at_least_one_student)
    break

  part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
  fromaddr = "ne-pas-repondre@themoocagency.com"
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = email
  msg['Subject'] = "BMD_grade_report"
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


# exemple Koa-qualif
# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/bmd/lms/static/utils/completion_report.py

# Exams occur everyday, send grade report after todays exam. Choose the right time to send a grade report in crontab. 
