# -*- coding: utf-8 -*-
#!/usr/bin/env python
import importlib
import sys
importlib.reload(sys)
import os

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
import glob
from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade
from lms.djangoapps.wul_apps.models import WulCourseEnrollment

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.course_groups.cohorts import get_cohort
from lms.djangoapps.courseware.models import StudentModule
from datetime import datetime

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


if course_ids[0] == 'course-v1:af-brasil+OFM+01' :
  HEADERS_SECTION = ['Quiz Unité 1', 'Quiz Unité 2', 'Quiz Unité 3', 'Quiz Unité 4', 'Quiz Unité 5']
elif course_ids[0] == 'course-v1:af-brasil+go+2024' :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Apresentações', 'Quiz Família & Pets', 'Quiz Tempo', 'Quiz Festas & Tradições', 'Quiz Estudos', 'Quiz Trabalho',  'Quiz Lazer',  'Quiz Saúde', 'Quiz Viagem', 'Quiz Cidade', 'Quiz Casa', 'Quiz Gastronomia', 'Quiz Moda', 'Quiz DELF A1']
elif course_ids[0] == 'course-v1:af-brasil+go+degustation' :
  HEADERS_SECTION = ['Quiz Primeiros Passos']
else :
  HEADERS_SECTION = ['Quiz Primeiros Passos', 'Quiz Destination Paris', 'Quiz Apresentações', 'Quiz Tour Eiffel & Champ de Mars', 'Quiz Família & Pets', 'Quiz Château de Versailles', 'Quiz Tempo', 'Quiz Stade de France', 'Quiz Festas & Tradições', 'Quiz Yvelines', 'Quiz Estudos', 'Quiz Seine-Saint-Denis', 'Quiz Trabalho', 'Quiz Paris La Défense Arena', 'Quiz Lazer', 'Quiz Stades en France', 'Quiz Saúde', 'Quiz Invalides & Pont d\'Iéna', 'Quiz Viagem', 'Quiz Arenas Paris Sud', 'Quiz Cidade', 'Quiz Ailleurs en France', 'Quiz Casa', 'Quiz La Concorde', 'Quiz Gastronomia', 'Quiz Arena Bercy', 'Quiz Moda', 'Quiz Grand Palais', 'Quiz DELF A1', 'Quiz Arena Porte de La Chapelle']

HEADERS_USER.extend(HEADERS_SECTION)
HEADERS_USER.append('Note globale (en %)')

HEADERS_AFTER_SECTION = [u"Certificate date", u"Time tracking", u"Days logged", u"Cohort"]
HEADERS_USER.extend(HEADERS_AFTER_SECTION)



# Survey
if course_ids[0] == 'course-v1:af-brasil+go+2024' :
  HEADERS_SECTION = ['Primeiros Passos Survey L1_1','Primeiros Passos Survey L1_2','Primeiros Passos Survey L1_3','Primeiros Passos Survey L1_4','Apresentações Survey L2_1','Apresentações Survey L2_2','Apresentações Survey L2_3','Apresentações Survey L2_4','Família & Pets Survey L3_1','Família & Pets Survey L3_2','Família & Pets Survey L3_3','Família & Pets Survey L3_4','Tempo Survey L4_1','Tempo Survey L4_2','Tempo Survey L4_3','Tempo Survey L4_4','Festas & Tradições Survey L5_1','Festas & Tradições Survey L5_2','Festas & Tradições Survey L5_3','Festas & Tradições Survey L5_4','Estudos Survey L6_1','Estudos Survey L6_2','Estudos Survey L6_3','Estudos Survey L6_4','Trabalho Survey L7_1','Trabalho Survey L7_2','Trabalho Survey L7_3','Trabalho Survey L7_4','Lazer Survey L8_1','Lazer Survey L8_2','Lazer Survey L8_3','Lazer Survey L8_4','Saúde Survey L9_1','Saúde Survey L9_2','Saúde Survey L9_3','Saúde Survey L9_4','Viagem Survey L10_1','Viagem Survey L10_2','Viagem Survey L10_3','Viagem Survey L10_4','Cidade Survey L11_1','Cidade Survey L11_2','Cidade Survey L11_3','Cidade Survey L11_4','Casa Survey L12_1','Casa Survey L12_2','Casa Survey L12_3','Casa Survey L12_4','Gastronomia Survey L13_1','Gastronomia Survey L13_2','Gastronomia Survey L13_3','Gastronomia Survey L13_4','Moda Survey L14_1','Moda Survey L14_2','Moda Survey L14_3','Moda Survey L14_4','DELF A1 Survey L15_1','DELF A1 Survey L15_2','DELF A1 Survey L15_3','DELF A1 Survey L15_4',]
  HEADERS_USER.extend(HEADERS_SECTION)


HEADER = HEADERS_USER

all_users_data = {}

for course_id in course_ids:

  #  les fichiers dans le dossiers data/ ne sont pas complet 
  csv_file_path = '/edx/var/edxapp/media/microsites/af-brazil/data/old/' + str(course_id) +'.csv'
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
  course_data = {}


  list_of_survey = StudentModule.objects.filter(course_id__exact=course_id, module_type__exact="survey").order_by().values('student_id', 'state', 'module_state_key')


  for i in range(len(course_enrollments)):
    user = course_enrollments[i].user
    user_data = []
    enrollment = course_enrollments[i]


    UserGrade = ['CFL1', 'DFL1', 'CFL2', 'DFL2', 'CFL3', 'DFL3', 'CFL4', 'DFL4', 'CFL5', 'DFL5', 'CFL6', 'DFL6', 'CFL7', 'DFL7', 'CFL8', 'DFL8', 'CFL9', 'DFL9', 'CFL10', 'DFL10', 'CFL11', 'DFL11', 'CFL12', 'DFL12', 'CFL13', 'DFL13', 'CFL14', 'DFL14', 'CFL15', 'DFL15']
    survey_block_list = False

    if course_ids[0] == 'course-v1:af-brasil+OFM+01' :
      UserGrade = ['QU1', 'QU2', 'QU3', 'QU4', 'QU5']

    if course_ids[0] == 'course-v1:af-brasil+go+2024' :
      UserGrade = ['CFL1', 'CFL2', 'CFL3', 'CFL4', 'CFL5', 'CFL6', 'CFL7', 'CFL8', 'CFL9', 'CFL10', 'CFL11', 'CFL12', 'CFL13', 'CFL14', 'CFL15']
      survey_block_list = [
        'block-v1:af-brasil+go+2024+type@survey+block@9f65f9ec2cfb4fb3a031f5c0930e572e', 
        'block-v1:af-brasil+go+2024+type@survey+block@6a1075442b844f8f84ec0e8ef5d172e5', 
        'block-v1:af-brasil+go+2024+type@survey+block@3dba2a53822d45d5b9ec11f8d291b331', 
        'block-v1:af-brasil+go+2024+type@survey+block@7b1c13d7e39d447086885b4cd9f30520', 
        'block-v1:af-brasil+go+2024+type@survey+block@1a8051a0b4fb4f77b48e5a163639a1ac', 
        'block-v1:af-brasil+go+2024+type@survey+block@1bc5f3006fd74c1bb0b4dfba7770b80f', 
        'block-v1:af-brasil+go+2024+type@survey+block@8db91034111740a1be9b9af05b67abac', 
        'block-v1:af-brasil+go+2024+type@survey+block@804b94360cd044e98a777a7307caf317', 
        'block-v1:af-brasil+go+2024+type@survey+block@30512b8b77f740a0b1ea9acee6d690b2', 
        'block-v1:af-brasil+go+2024+type@survey+block@eb0f9fe99f664d54a916b66b5d3790da',
        'block-v1:af-brasil+go+2024+type@survey+block@e55b1b461a8146afa856f7b50de538d1',
        'block-v1:af-brasil+go+2024+type@survey+block@b930084f0da94f4490554d201c588b1d',
        'block-v1:af-brasil+go+2024+type@survey+block@7a221d1a32024da7b099b3c6f3342726',
        'block-v1:af-brasil+go+2024+type@survey+block@1f9d35f98f114dc69997e654824a87ac',
        'block-v1:af-brasil+go+2024+type@survey+block@21ebe3b084034f94a6b3f09505ca5063'
      ]

    if course_ids[0] == 'course-v1:af-brasil+go+degustation' :
      UserGrade = ['CFL1']

    user_CF_data = json.loads(user.profile.custom_field)

    if str(user.email).find('@yopmail') != -1 or str(user.email).find('@weuplearning') != -1 or str(user.email).find('@themoocagency') != -1 :
      continue



    fullname = user.profile.name
    if fullname == '' :
      fullname = user_CF_data.get('name', '')

    user_data.append(fullname)
    user_data.append(user.email)
    user_data.append(user.username)

    try :
      date_str = user_CF_data['success_date_' + course_id]
      date_obj = datetime.strptime(date_str, "%Y-%m-%d")
      certificate_date = date_obj.strftime("%d/%m/%Y")
    except :
      certificate_date = 'n.a.'


    for key in TECHNICAL_HEADER :
      try :
        user_data.append(user_CF_data[key])
      except :
        user_data.append('n.a.')

    try :
      user_data.append(user.date_joined.strftime('%d/%m/%Y'))
    except :  
      user_data.append('n.a.')

    try :
      user_data.append(user.last_login.strftime('%d/%m/%Y'))
    except :  
      user_data.append('n.a.')



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



    # TimeTracking
    try:
      wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
      global_time_tracking = str(wul_course_enrollment.global_time_tracking // 60)
      days_logged = str(wul_course_enrollment.detailed_time_tracking.count(',')+1)
    except:
      global_time_tracking = "0"
      days_logged = "0"

    time_tracking = []
    time_tracking.append(global_time_tracking)
    time_tracking.append(days_logged)



    # Cohort
    cohort = get_cohort(user, course_key, assign=True, use_cached=False)
    if cohort :
      cohort = str(cohort)
    else :
      cohort = 'n.a.'



    # Survey
    formated_survey_block_list = []
    empty_value = ['','','','']

    if survey_block_list :
      for module in list_of_survey :
        if module['student_id'] == user.id : 
          module_state = json.loads(module["state"])
          survey_block_list = [ module_state if str(module['module_state_key']) == survey_block and module.get("state")  else survey_block for survey_block in survey_block_list ]


      for element in survey_block_list : 
        if isinstance(element, dict) and element['choices']:
          for key, value in element['choices'].items() : 
            survey_value = value.replace('Y', '1').replace('N', '2').replace('M', '3').replace('1730402209980', '4')
            formated_survey_block_list.extend(survey_value)
        else : 
          formated_survey_block_list.extend(empty_value)






    data = []
    data.extend(user_data)
    data.extend(UserGrade)
    data.append(globalGradeStr)
    data.append(certificate_date)
    data.extend(time_tracking)
    data.append(cohort)
    data.extend(formated_survey_block_list)


    course_data[str(user.id)] = data

  all_users_data[course_id]= course_data



# Write CSV
timestr = time.strftime("%Y_%m_%d")
filename = f'/edx/var/edxapp/media/microsites/af-brazil/csv/{course_ids[0]}/{timestr}_af-brasil_grade_report.csv'

csv_dir = f'/edx/var/edxapp/media/microsites/af-brazil/csv/{course_ids[0]}/'


# Supprimer les fichiers CSV de plus de 3 jours
def delete_old_csv_files(directory, days=3):
  now = time.time()
  cutoff = now - (days * 86400)  # 86400 secondes dans un jour

  for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)

    if os.path.isfile(file_path):
      file_stat = os.stat(file_path)
      if file_stat.st_mtime < cutoff:
        log.info(f'Suppression du fichier: {file_path}')
        os.remove(file_path)

delete_old_csv_files(csv_dir)


with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
  writer = csv.writer(csvfile, delimiter=';')
  writer.writerow(HEADER)

  for k, course_id in all_users_data.items():

    for user_id, user_data in course_id.items():
      writer.writerow(user_data)


with open(filename, 'rb') as f:
  attachment = f.read()


log.info('------------> Finish calculating grades and writing CSV report')



# New grade report every 2 hours
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+PP+CPB 
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+PP+2024 
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+PP+CPB01
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+OFM+01
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+PP+TB
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+go+2024
# 0 */2 * * * /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_csv.py course-v1:af-brasil+go+degustation



# https://af-brazil.weup.in/wul_apps/csv_data_weup/course-v1:af-brasil+PP+CPB
# /edx/var/edxapp/media/microsites/af-brazil/csv/course-v1:af-brasil+PP+TB/2024_10_30_af-brasil_grade_report.csv


# Survey tests :
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/grade_report_script_survey.py  course-v1:af-brasil+go+2024

