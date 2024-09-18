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

import csv 
import json
import time
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade
from lms.djangoapps.wul_apps.models import WulCourseEnrollment

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import logging
log = logging.getLogger()

course_ids = sys.argv[1].split(";")

try :
  emails = sys.argv[2].split(";")
except :
  emails = []


org = "af-brasil"
register_form = configuration_helpers.get_value_for_org(org, 'FORM_EXTRA')

# Get headers
HEADERS_USER = [u"Nom complet", u"Email",u"Username", u"Phone",u"Nearest AF", u"Registration date", u"Last login"]
HEADERS_FORM = []


if register_form is not None:
  for row in register_form:
    if row.get('type') is not None:
      HEADERS_FORM.append(row.get('name'))

TECHNICAL_HEADER = list(HEADERS_FORM)

UserGrade = ['CFL1','DFL1','CFL2','DFL2','CFL3','DFL3','CFL4','DFL4','CFL5','DFL5','CFL6','DFL6','CFL7','DFL7','CFL8','DFL8','CFL9','DFL9','CFL10','DFL10','CFL11','DFL11','CFL12','DFL12','CFL13','DFL13','CFL14','DFL14','CFL15','DFL15']


if course_ids[0] == 'course-v1:af-brasil+PP+CPB' :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Destination Paris', 'Quiz Apresentações', 'Quiz Tour Eiffel & Champ de Mars', 'Quiz Família & Pets', 'Quiz Château de Versailles', 'Quiz Tempo', 'Quiz Stade de France', 'Quiz Festas & Tradições', 'Quiz Yvelines', 'Quiz Estudos', 'Quiz Seine-Saint-Denis', 'Quiz Trabalho', 'Quiz Paris La Défense Arena', 'Quiz Lazer', 'Quiz Stades en France', 'Quiz Saúde', 'Quiz Invalides & Pont d\'Iéna', 'Quiz Viagem', 'Quiz Arenas Paris Sud', 'Quiz Cidade', 'Quiz Ailleurs en France', 'Quiz Casa', 'Quiz La Concorde', 'Quiz Gastronomia', 'Quiz Arena Bercy', 'Quiz Moda', 'Quiz Grand Palais', 'Quiz DELF A1', 'Quiz Arena Porte de La Chapelle']

elif course_ids[0] == 'course-v1:af-brasil+PP+CPB01' :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Destination Paris', 'Quiz Apresentações', 'Quiz Tour Eiffel & Champ de Mars', 'Quiz Família & Pets', 'Quiz Château de Versailles', 'Quiz Tempo', 'Quiz Stade de France', 'Quiz Festas & Tradições', 'Quiz Yvelines', 'Quiz Estudos', 'Quiz Seine-Saint-Denis', 'Quiz Trabalho', 'Quiz Paris La Défense Arena', 'Quiz Lazer', 'Quiz Stades en France', 'Quiz Saúde', 'Quiz Invalides & Pont d\'Iéna', 'Quiz Viagem', 'Quiz Arenas Paris Sud', 'Quiz Cidade', 'Quiz Ailleurs en France', 'Quiz Casa', 'Quiz La Concorde', 'Quiz Gastronomia', 'Quiz Arena Bercy', 'Quiz Moda', 'Quiz Grand Palais', 'Quiz DELF A1', 'Quiz Arena Porte de La Chapelle']

elif course_ids[0] == 'course-v1:af-brasil+PP+TB' :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Destination Paris', 'Quiz Apresentações', 'Quiz Tour Eiffel & Champ de Mars', 'Quiz Família & Pets', 'Quiz Château de Versailles', 'Quiz Tempo', 'Quiz Stade de France', 'Quiz Festas & Tradições', 'Quiz Yvelines', 'Quiz Estudos', 'Quiz Seine-Saint-Denis', 'Quiz Trabalho', 'Quiz Paris La Défense Arena', 'Quiz Lazer', 'Quiz Stades en France', 'Quiz Saúde', 'Quiz Invalides & Pont d\'Iéna', 'Quiz Viagem', 'Quiz Arenas Paris Sud', 'Quiz Cidade', 'Quiz Ailleurs en France', 'Quiz Casa', 'Quiz La Concorde', 'Quiz Gastronomia', 'Quiz Arena Bercy', 'Quiz Moda', 'Quiz Grand Palais', 'Quiz DELF A1', 'Quiz Arena Porte de La Chapelle']

elif course_ids[0] == 'course-v1:af-brasil+OFM+01' :
  HEADERS_SECTION = ['Quiz Unité 1', 'Quiz Unité 2','Quiz Unité 3','Quiz Unité 4','Quiz Unité 5']
  UserGrade = ['QU1', 'QU2', 'QU3', 'QU4', 'QU5']

else  :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Destination Paris', 'Quiz Apresentações', 'Quiz Tour Eiffel & Champ de Mars', 'Quiz Família & Pets', 'Quiz Château de Versailles', 'Quiz Tempo', 'Quiz Stade de France', 'Quiz Festas & Tradições', 'Quiz Yvelines', 'Quiz Estudos', 'Quiz Seine-Saint-Denis', 'Quiz Trabalho', 'Quiz Paris La Défense Arena', 'Quiz Lazer', 'Quiz Stades en France', 'Quiz Saúde', 'Quiz Invalides & Pont d\'Iéna', 'Quiz Viagem', 'Quiz Arenas Paris Sud', 'Quiz Cidade', 'Quiz Ailleurs en France', 'Quiz Casa', 'Quiz La Concorde', 'Quiz Gastronomia', 'Quiz Arena Bercy', 'Quiz Moda', 'Quiz Grand Palais', 'Quiz DELF A1', 'Quiz Arena Porte de La Chapelle']


HEADERS_USER.extend(HEADERS_SECTION)
HEADERS_USER.append('Note globale (en %)')

HEADERS_AFTER_SECTION = [u"Certificate date", u"Time tracking", u"Days logged"]
HEADERS_USER.extend(HEADERS_AFTER_SECTION)

HEADER = HEADERS_USER


all_users_data = {}


for course_id in course_ids:

  csv_file_path = '/edx/var/edxapp/media/microsites/af-brazil/data/' + str(course_id) +'.csv'
  csv_data = False
  csv_user_grade = []
  csv_grade_index = 0

  try :
    with open(csv_file_path, newline='') as csvfile:
      csvreader = csv.reader(csvfile, delimiter=';')
      csv_data = []
      for row in csvreader:
        csv_data.append(row)
  except :
    csv_data = False


  course_key = CourseLocator.from_string(course_id)
  course = get_course_by_id(course_key)
  course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
  course_name = course.display_name_with_default

  course_data = {}

  for i in range(len(course_enrollments)):
    user = course_enrollments[i].user
    user_data = []
    enrollment = course_enrollments[i]
    

    user_CF_data = json.loads(user.profile.custom_field)

    # if str(user.email).find('@yopmail') != -1 or str(user.email).find('@weuplearning') != -1 or str(user.email).find('@themoocagency') != -1 :
    #   continue

    user_data.append(user.profile.name)
    user_data.append(user.email)
    user_data.append(user.username)

    try :
      certificate_date = user_CF_data["certificate_date_"+str(course_id.replace("-","_").replace(":","_").replace("+","_"))]
    except :
      certificate_date = 'n.a.'


    for key in TECHNICAL_HEADER :
      try :
        user_data.append(user_CF_data[key])
      except :
        user_data.append('n.a.')


    user_data.append(user.date_joined.strftime('%d %b %y'))
    user_data.append(user.last_login.strftime('%d %b %y'))



    # Grade  -  Il faut re-calculer la note pour prendre en compte l'historique des données 
    gradesTest = check_best_grade(user, course, force_best_grade=True)

    for section in gradesTest.summary['section_breakdown'] :
      UserGrade = [str(section['percent']) if grade == section['label'] else grade for grade in UserGrade]


    csv_user_grade = []
    if csv_data :
      for user_data_csv in csv_data :
        if len(user_data_csv)>1 and user.email == user_data_csv[1] :

          csv_user_grade = user_data_csv[4:-7]
          i=0
          for grade_section_csv in csv_user_grade : 
            if grade_section_csv > UserGrade[i] :
              UserGrade[i] = grade_section_csv
            i+=1

          continue

    sumGrade = 0
    numGrade = 0
    for grade in UserGrade :
      sumGrade += float(grade)*100
      numGrade +=1 

    try:
      globalGrade = int(sumGrade / numGrade )
      globalGradeStr = str(globalGrade) +'%'
    except:
      globalGradeStr = '0%'


    #TimeTracking
    try:
      wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
      global_time_tracking = wul_course_enrollment.global_time_tracking
      days_logged = wul_course_enrollment.detailed_time_tracking.count(',')+1
    except:
      global_time_tracking = 0

    time_tracking = []
    time_tracking.append(global_time_tracking)
    time_tracking.append(days_logged)



    data = { "general": user_data, "grade_section": UserGrade, "grade_global" :globalGradeStr, "certificate_date": certificate_date, "time_tracking" : time_tracking }

    course_data[str(user.id)] = data

  all_users_data[course_id]= course_data


# WRITE XLS
timestr = time.strftime("%Y_%m_%d")
wb = Workbook()
sheet = wb.active
sheet.title= 'Rapport de notes'
filename = '/edx/var/edxapp/media/microsites/af-brazil/csv/{}_af-brasil_grade_report.xlsx'.format(timestr)


correspondance_CF = {
  'true' : 'Oui',
  'false' : 'Non',
  'bac_5' : 'Bac +5',
  'bac_2_3' : 'Bac +2/+3',
  'bac' : 'Bac',
  'bac_general' : 'Bac général',
  'bac_technologique' : 'Bac technologique',
  'bacpro' : 'Bac professionnel',
  'bep_cap' : 'BEP/CAP',
  'no_level' : 'Pas de diplôme',
  'oui' : 'Oui',
  'non' : 'Non'
}


for i, header in enumerate(HEADER):
  sheet.cell(1, i+1, header)
  sheet.cell(1, i+1).font = Font(b=True, color="000000")


j=2

for k, course_id in all_users_data.items():
  
  for key, user in course_id.items():

    for i in range(len(user['general'])):
      if user['general'][i] in correspondance_CF:
        sheet.cell(j, i+1, correspondance_CF[user['general'][i]])
      else :
        sheet.cell(j, i+1, user['general'][i])

    for i in range(len(user['grade_section'])):
      sheet.cell(j, i+8, user['grade_section'][i])

    sheet.cell(j, i+9, user['grade_global'])
    sheet.cell(j, i+10, user['certificate_date'])

    for i in range(len(user['time_tracking'])):
      sheet.cell(j, i+40, user['time_tracking'][i])

    j += 1


# SEND MAILS
course_names_html = []
for course_id in course_ids: 
  course = get_course_by_id(CourseLocator.from_string(course_id)) 
  course_names_html.append("<li>"+ str(course.display_name_with_default)+"</li>")

output = BytesIO()
wb.save(output)


# Supprimer les anciens fichiers xlsx en ne gardant que les 2 plus récents
folder_path = '/edx/var/edxapp/media/microsites/af-brazil/csv/'
file_extension = '*.xlsx'
files = glob.glob(os.path.join(folder_path, file_extension))
files.sort(key=os.path.getmtime)
if len(files) > 2:
  for old_file in files[:-2]:
    try:
      os.remove(old_file)
      log.info(f"Fichier supprimé : {old_file}")
    except OSError as e:
      log.error(f"Erreur lors de la suppression du fichier {old_file}: {e}")

wb.save(filename)

_files_values = output.getvalue()
course_names_html = ''.join(course_names_html)

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note concernant le cours : "+ course_names_html +"<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"

for email in emails:

  part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
  fromaddr = "ne-pas-repondre@themoocagency.com"
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = email
  msg['Subject'] = u"Rapport de notes AF Brasil"
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
# pas de cours .... 

# PROD
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script.py course-v1:af-brasil+PP+CPB 'cyril.adolf@weuplearning.com' 


# New grade report every 2 hours
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script.py course-v1:af-brasil+PP+CPB 

