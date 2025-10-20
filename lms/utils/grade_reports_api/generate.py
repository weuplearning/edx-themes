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
import datetime

import report_config
#############################################################
#         ^ SETUP ENVIRONNEMENT VARIABLE FOR KOA ^          #
#                START BEYOND THIS LINE                     #
#############################################################


import json
import time
import datetime

import pprint
import isodate


from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_course_by_id
# from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from lms.djangoapps.courseware.models import StudentModule


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

timestamp_startup = time.time()



import logging
log = logging.getLogger()



all_users_data = {}

umn_scorm_list = report_config.umn_scorm_list


empty_str = "n.a."
empty_str = "n/a"


# /edx/app/edxapp/edx-platform/common/djangoapps/student/models.py : 1152
# Donnees necessaires : email , notes, time tracking, connexions, inscription, thats IT
#course_ids = [ 'course-v1:umn+pn+02','course-v1:umn+test+test','course-v1:umn+pi+01']
course_ids = [ 'course-v1:umn+pn+02','course-v1:umn+pi+01']

#course_keys = []
#for course_id in course_ids:
#  course_key = CourseLocator.from_string(course_id)
#  course_keys.append(course_key)


colors = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
]
reset = "\033[0m"

print(course_ids)




from xblock.runtime import Runtime
from opaque_keys.edx.keys import UsageKey
from xblock.field_data import DictFieldData
from xblock.core import XBlock
from xmodule.modulestore.django import modulestore



scorm_lookup_table = {
"block-v1:umn+pi+01+type@scorm+block@6c738f84a4fc4c60af3e96b4f48393e2" :"A1 The need of Energy",
"block-v1:umn+pi+01+type@scorm+block@ea25c0bf019c4af896071740719b4496" :"A2 From radioactivity to nuclear fission: principles",
"block-v1:umn+pi+01+type@scorm+block@ba2ce7a4e0e941a1a00929b546e93113" :"A3 How does a Nuclear Power Reactor work ?",
"block-v1:umn+pi+01+type@scorm+block@5154f8203dff49a5b8e05d7a10918061" :"A4 Nuclear energy around the world",
"block-v1:umn+pi+01+type@scorm+block@96ddd111f9194341b3d5bcca337f1157" :"A5 Nuclear energy in France",
"block-v1:umn+pi+01+type@scorm+block@8da3c6467f2d4f41bcebffffc1704f3b" :"A6 Nuclear safety, safety culture and radiation protection equipment",
"block-v1:umn+pi+01+type@scorm+block@bcc00768317549718cb6709036c5cad6" :"A7 Nuclear professions",
"block-v1:umn+pi+01+type@scorm+block@1f1fd4a4b3744566a4c4e5e722dc4fc4" :"A8 The majors nuclear accidents in the world",
"block-v1:umn+pi+01+type@scorm+block@c2abc2bc914143d6886d46e30f31175a" :"A9 The different stakeholders in nuclear safety",
"block-v1:umn+pi+01+type@scorm+block@252805a7295a4fcb82e9e85ed328e482" :"B1 Uranium supply: mines and quarries",
"block-v1:umn+pi+01+type@scorm+block@2fd4a76e074c4f9a8ab286cff1a2aadf" :"B2 Focus on the fuel",
"block-v1:umn+pi+01+type@scorm+block@3b09d1ba219d4cc180db58cab7281e0f" :"B3 The fuel cycle and its closure",
"block-v1:umn+pi+01+type@scorm+block@7f9e9f4cf0b14e0db688053c0e47857a" :"B4 The PWR technology - Main circuits and safety systems",
"block-v1:umn+pi+01+type@scorm+block@786750b68cda484da5011a56f8a9619f" :"B5 Codes Standards and Regulation",
"block-v1:umn+pi+01+type@scorm+block@c77983e412324fd5b67ac8b550c4981c" :"B6 Design and Manufacturing of big components",
"block-v1:umn+pi+01+type@scorm+block@9bb79e4e57af426ea4b4818618580563" :"B7 The nuclear supply chain",
#"block-v1:umn+pi+01+type@scorm+block@fa43b931c551446d81d7c33c92516a85" :"B8 Serious Game - Exploration of a nuclear power plant",
"block-v1:umn+pi+01+type@scorm+block@b9e0ff393b7b4127be00371ddd771557" :"C1 The 'Grand Carénage' and the EPR2 program",
"block-v1:umn+pi+01+type@scorm+block@c5d1e4c46b534a74a6aad70139a90547" :"C2 The 'Grand Carénage' safety recommandations",
"block-v1:umn+pi+01+type@scorm+block@4be97424897445ca9190e95bd8cd17df" :"C3 EPR2 the safety benefits",
"block-v1:umn+pi+01+type@scorm+block@78fe58109a504d1cb3c526b69522c440" :"C4 The operation of an INB, role and challenge",
"block-v1:umn+pi+01+type@scorm+block@11750ed5b20d466bb8174fe50001251f" :"C5 The major risk: fire",
"block-v1:umn+pi+01+type@scorm+block@af11779f19d54883802ae3020968e36d" :"C6 The regulation and is impact on nuclear reactor operation",
#"block-v1:umn+pi+01+type@scorm+block@5226ebf71e7c49c8bd7e586022128d9e" :"C8 Serious Game - Operation of a nuclear power plant",
"block-v1:umn+pi+01+type@scorm+block@0984d8859c4c4c2f808a4a41a02cba34" :"D1 The challenges of dismantling and storage",
"block-v1:umn+pi+01+type@scorm+block@0b900cee83944ff880f459e234a7242c" :"D2 The different storage facilities in France and their characteristics",
"block-v1:umn+pi+01+type@scorm+block@460198f9fd2c48c29e457b84bfc4e347" :"D3 The regulatory framework for dismantling and the phasing",
"block-v1:umn+pi+01+type@scorm+block@1d7c297fdeeb42d0b77354fc415e5348" :"D4 Careers in decommissioning",
"block-v1:umn+pi+01+type@scorm+block@5904c9063f7748e0ba7a9e13d138cb0b" :"D5 The future of nuclear power: generation IV reactors",
"block-v1:umn+pi+01+type@scorm+block@f608d35f323443648414896bb0ae48ee" :"D6 Focus on SMR and AMR",
"block-v1:umn+pi+01+type@scorm+block@0e6bed04c9894969811888b8bea544a0" :"D7 Nuclear Fusion - The Tokamak on the ITER Project",
"block-v1:umn+pi+01+type@scorm+block@ec81c17216d146b0a42cd35f49793241" :"D8 Careers in the future of nuclear power",
"block-v1:umn+pn+02+type@scorm+block@2cad17b664064248ac8a93388a464612" : "1.1 L'énergie nucléaire en France",
"block-v1:umn+pn+02+type@scorm+block@bf9933dc1f2f452690f6b90f82326bc6" : "1.2 Environnement : Les bâtiments constitutifs d'une centrale nucléaire",
"block-v1:umn+pn+02+type@scorm+block@d9686f98cf07492887129ad3fc4e64e5" : "1.3 Introduction aux différents circuits principaux et de sauvegarde",
"block-v1:umn+pn+02+type@scorm+block@fef1daca9a794568bd76f761a5b992d1" : "1.4 La production d'électricité",
"block-v1:umn+pn+02+type@scorm+block@5080c48db29844728b1887355cc09159" : "1.5 Balance of Plant BOP",
#"block-v1:umn+pn+02+type@scorm+block@f8c14e194f9b41b3b859d596c9a1c398" : "1.6 Serious Game 1 Introduction et fondements de l'énergie nucléaire",
"block-v1:umn+pn+02+type@scorm+block@730855c5f22c4857adce5831ce323ebb" : "2.1 La radioactivité",
"block-v1:umn+pn+02+type@scorm+block@3f16d65d916e40f0a9ee75a40ed8c30d" : "2.2 Le cycle du combustible",
"block-v1:umn+pn+02+type@scorm+block@6871056a6ee145819c109152413790ba" : "2.3 Le cycle du combustible Process",
"block-v1:umn+pn+02+type@scorm+block@d30a3b24ce5f48a4a4b90499841c2a5b" : "2.4 Le démantèlement et le stockage",
"block-v1:umn+pn+02+type@scorm+block@4e5ac4aba3cc4466b909ccc2246edc9a" : "3.1 Protection contre les rayonnements ionisants",
"block-v1:umn+pn+02+type@scorm+block@e618a3a9f7374586bb24ce31b0fd06bf" : "3.2 La défense en profondeur",
"block-v1:umn+pn+02+type@scorm+block@0513ab9c8ac7434787e95b8e1085a549" : "3.3 Fonctions de sûreté",
"block-v1:umn+pn+02+type@scorm+block@df86fd4c446c4923a3dd7b77a01d932b" : "3.4 Barrières de confinement",
"block-v1:umn+pn+02+type@scorm+block@aabd0c9d5afc4095bdc17fc1fdb2c17b" : "3.5 Arrêté INB et ASN : Un encadrement réglementaire",
"block-v1:umn+pn+02+type@scorm+block@d296cb76795a4ed79caa5384171507df" : "3.6 Qualité nucléaire",
"block-v1:umn+pn+02+type@scorm+block@c347c583b97c45748d8e96674dce61ba" : "3.7 Accidents majeurs",
#"block-v1:umn+pn+02+type@scorm+block@2e4c39dd6f5744cdb4e257f1061ef375" : "3.8 Serious game 2 Sécurité, sûreté, radioprotection et environnement",
"block-v1:umn+pn+02+type@scorm+block@912617e856a24a0f8fb6537485bae663" : "4.1 Les acteurs majeurs et les métiers du nucléaire",
"block-v1:umn+pn+02+type@scorm+block@572e16ef99d94d5899bd0ce028c052d0" : "4.2 Les innovations",
#"block-v1:umn+pn+02+type@scorm+block@12b33d71a4b847d79c1f751ebfef5e42" : "4.3 Serious Game 3",
## "block-v1:umn+test+test+type@scorm+block@fd4f25a734734497bc0111f6fd549a26" : "1.1 L'énergie nucléaire en France",
## "block-v1:umn+test+test+type@scorm+block@5fae2b299b0e47a48e8112d3b11aa615" : "1.2 Environnement : Les bâtiments constitutifs d'une centrale nucléaire",
## "block-v1:umn+test+test+type@scorm+block@dc3e413d33234a1dafd0bca06ae0c5e1" : "1.3 Introduction aux différents circuits principaux et de sauvegarde",
## "block-v1:umn+test+test+type@scorm+block@02915ef6d75747d1a04d87689a60542d" : "1.4 La production d'électricité",
## "block-v1:umn+test+test+type@scorm+block@b320c1c95f1f47cd8a9f63a441766f9a" : "1.5 Balance of Plant - BOP",
## #"block-v1:umn+test+test+type@scorm+block@f8c14e194f9b41b3b859d596c9a1c398" : "1.6 Serious Game 1 - Introduction et fondements de l'énergie nucléaire",
## "block-v1:umn+test+test+type@scorm+block@f67c1876fa8c46e49f37596711c1768b" : "2.1 La radioactivité",
## "block-v1:umn+test+test+type@scorm+block@cede2c08a2b24c09aeeab327522c1b09" : "2.2 Le cycle du combustible",
## "block-v1:umn+test+test+type@scorm+block@67c2292f054f4ad68702733b411dc6ca" : "2.3 Le cycle du combustible Process",
## "block-v1:umn+test+test+type@scorm+block@21c4ca65a2d54879bf843db10f1842f3" : "2.4 Le démantèlement et le stockage",
## "block-v1:umn+test+test+type@scorm+block@4e5ac4aba3cc4466b909ccc2246edc9a" : "3.1 Protection contre les rayonnements ionisants",
## "block-v1:umn+test+test+type@scorm+block@e618a3a9f7374586bb24ce31b0fd06bf" : "3.2 La défense en profondeur",
## "block-v1:umn+test+test+type@scorm+block@0513ab9c8ac7434787e95b8e1085a549" : "3.3 Fonctions de sûreté",
## "block-v1:umn+test+test+type@scorm+block@def1b70b68e4422cbe52694e68b3afa6" : "3.4 Barrières de confinement",
## "block-v1:umn+test+test+type@scorm+block@9d02fb2863954a3d95b867ee0e066c7c" : "3.5 Arrêté INB et ASN : Un encadrement réglementaire",
## "block-v1:umn+test+test+type@scorm+block@72922a0c6c054283b8e554baffa121d0" : "3.6 Qualité nucléaire",
## "block-v1:umn+test+test+type@scorm+block@c347c583b97c45748d8e96674dce61ba" : "3.7 Accidents majeurs",
## #"block-v1:umn+test+test+type@scorm+block@2e4c39dd6f5744cdb4e257f1061ef375" : "3.8 Serious game 2 - Sécurité, sûreté, radioprotection et environnement",
## "block-v1:umn+test+test+type@scorm+block@5d1cf5d6f4794bc1ad8821efee50c85b" : "4.1 Les acteurs majeurs et les métiers du nucléaire",
## "block-v1:umn+test+test+type@scorm+block@daa34dbada1441268b2106bfcf91817b" : "4.2 Les innovations",
## #"block-v1:umn+test+test+type@scorm+block@12b33d71a4b847d79c1f751ebfef5e42" : "4.3 Serious Game 3"
}

course_module_lookup = {
  "1" : 5,
  "2" : 4,
  "3" : 7,
  "4" : 2,
  "A" : 9,
  "B" : 7,
  "C" : 6,
  "D" : 8,
}
course_module_total_lookup = {
  "pi01" : 30,
  "pn02" : 18
}


course_prefix_table = {
"block-v1:umn+test+test+type" : "PF1",
"block-v1:umn+pn+02+type" : "PF2",
"block-v1:umn+pi+01+type" : "PMI"
}



def get_scorm_name(key):
  block_key = str(key)
  try:
    name = scorm_lookup_table[block_key]

    # custom UMN override
    name = name[:3]
    name = course_prefix_table[str(block_key.split('@')[0])] + '.' + name

  except:
    return None
  return name


def format_score_percent(value):
  # ex : 0.53333333333 -> 53.33 -> "53,33%"
  score = value

  if(score == '0.0'):
    score = 0
  
  score = score*100
  score = round(score ,2)
  score = str(score).replace('.',',') 
  score = str(score) + '%'
  return score

def parse_timetracking(seconds):
  # input is integer of seconds
  hours, remainder = divmod(seconds, 3600)
  minutes, secs = divmod(remainder, 60)
  formatted_time = f"{hours:02}:{minutes:02}:{secs:02}"
  return formatted_time


def parse_course_id(courseid):
  courseid = str(courseid)
  elems = courseid.split(':umn+')
  del elems[0]
  courseid = elems[0]
  courseid = courseid.replace('+','')
  return courseid


timestamp_begin = time.time()
enrollments = CourseEnrollment.objects.filter(course_id__in=course_ids)
global_user_amount = len(enrollments)
max_users = 30



timestamp_query = time.time()
#enrollments = enrollments[:max_users]

students = {}

for i, e in enumerate(enrollments):
    print(f'{i}/{len(enrollments)}')
    course_data = {
    }

    # 20 = melanie
    #if e.user.id != 403113:
    #  continue


    color = colors[i % len(colors)]  # cycle through colors
    #print(f"{color}",end='')
    #print(f"{i} {e.user.id} {e.user.email} {e.course_id} {e.user.last_login}",)


    if e.user.email.find('@yopmail') != -1 or e.user.email.find('@weuplearning') != -1 or e.user.email.find('@themoocagency') != -1:
      continue

    #try:
    #  print(f" {e.user.id} {e.user.email} {e.course_id} {e.user.last_login.strftime('%Y-%m-%d %H:%M:%S')}",end='')
    #except:
    #  print(f"error on {e.user.email}")
    #students["email"]


    try:
      wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=e.user, course_enrollment_edx__course_id=e.course_id)
      global_time_tracking = wul_course_enrollment.global_time_tracking
    except:
      global_time_tracking = 0
      
    


    list_of_student_modules = StudentModule.objects.filter(course_id__exact=e.course_id, module_type__exact="scorm", student_id=e.user.id).order_by().values('module_state_key', 'state')
    
    
    
    #print('------------------------------')
    ##firstmod = list_of_student_modules[0]
    ##print(firstmod)
    #print('------------------------------')

    #list_of_student_modules = StudentModule.objects.filter(course_id__exact=e.course_id, module_type__exact="scorm", student_id=e.user.id)
   # print(f" {len(list_of_student_modules)} modules",end='') 

    module_scores = {}

    for m in list_of_student_modules:
      #print('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
      #print(json.dumps(m))
      #print('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')

      module_state = json.loads(m["state"])
      
      #print('---- module state ---')
      #print(module_state)
      #print('')
      #print('---- module state JSON ---')
      #module_state['scorm_data']['cmi.suspend_data'] = ''
      #print(json.dumps(module_state))
      #print('---------------------')
      ##print(module_state['scorm_data']['cmi.session_time'])
      
      module_score = '0.0'
      try:
        module_score = module_state['lesson_score']
      except:
        pass
      module_key = str(m['module_state_key'])
      
      module_score = format_score_percent(module_score)

      module_string = get_scorm_name(module_key)
      if module_string == None:
        continue
      course_data[module_string]= module_score
      #print(f"module : {str(m['module_state_key'])} = {str(module_score)} ")
      #module_scores[str(m['module_state_key'])]:  str(module_score)

    #print(module_scores)

    if e.user.id not in students:
      try:
        d_register_time = e.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
      except:
        d_register_time  = ""

      try:
        d_last_login = e.user.last_login.strftime('%Y-%m-%d %H:%M:%S')
      except:
        d_last_login = ""
      students[e.user.id] = {
        "email": e.user.email,
        "register_time" :d_register_time,
        "last_login": d_last_login,
        "global_time_tracking": parse_timetracking(global_time_tracking),
        "courses" : {}
        }



    cid = str(e.course_id)
    cid = parse_course_id(e.course_id)
    
    #print(f" cours id is  {cid}")
    #print(students[e.user.id])
    students[e.user.id]["courses"][cid] = course_data


    #print(f"{reset}")
    #print(type(students))

    #pprint.pprint(students)






#### GET AVG FOR EACH MODULE GROUP




for student in students:
  #print(student)
  courses = students[student]['courses']
  for course in courses:
    modules_note_dict = {}
    print('course')
    print(course)
    notes = students[student]['courses'][course]
    course_total_score = 0.0
    note_counter = 0
    
    for note_entry in notes:
      note_counter += 1
      note = students[student]['courses'][course][note_entry]
      note_entry = note_entry.split('.')[1]
      note_group_id = note_entry
      note_group_id = note_group_id[0]

      try:
        test = modules_note_dict[note_group_id] 
        print(test)
      except KeyError:
        modules_note_dict[note_group_id] = ''

      modules_note_dict[note_group_id] += (note )
      # reparse note in percent to proper usable data 
      
      print(f'={note_group_id} - {note}')
    
    print(modules_note_dict)
    for group_id in modules_note_dict:
      print(group_id)
      content = modules_note_dict[group_id]
      notes = content.split('%')
      notes.remove("")
      print(notes)
      notes_parsed = []
      for note in notes:
        note = note.replace(',', '.')
        notes_parsed.append(float(note))
      acc = 0.0
      for note in notes_parsed:
        acc += note
      
      print(notes_parsed)
      print(f"got {len(notes_parsed)} out of {course_module_lookup[str(group_id)]} ")
      avg_module = acc/course_module_lookup[str(group_id)]
      avg_module = round(avg_module,2)
      avg_module = str(avg_module)
      avg_module = avg_module.replace('.', ',') + "%"
      module_average_identifer = f"M{group_id}_progression"
      print(f" {module_average_identifer} : {avg_module}")
      students[student]['courses'][course][module_average_identifer] = avg_module





#################################################################


print('#######################################################')
print('Processing Total progression for each course')


for student in students:
  #print(student)
  courses = students[student]['courses']
  for course in courses:
    print('course')
    print(course)
    notes = students[student]['courses'][course]
    course_total_score = 0.0
    note_counter = 0
    for note_entry in notes:
      if "progression" in note_entry:
        continue
      print(f"e {note_entry}")
      note_counter += 1
      note = students[student]['courses'][course][note_entry]
      # reparse note in percent to proper usable data 
      parsed_note = note
      parsed_note = parsed_note.strip().replace('%', '')
      parsed_note = parsed_note.replace(',', '.')
      parsed_note = float(parsed_note)
      course_total_score += parsed_note
    
    if((note_counter == 0) or (course_total_score == 0.0)):
      course_total = 0
    else:
      print(f"::: {course} ")
      course_total_module_count= course_module_total_lookup[course]
      print(f' attempting {course_total_score}/{course_total_module_count} ')
      course_total = course_total_score / course_total_module_count
      course_total = round(course_total,2)
    
    # now reparse format...
    course_total = str(course_total)
    course_total = course_total.replace('.', ',')
    course_total = course_total+'%'
    students[student]['courses'][course]['course_progression'] = course_total
    

print('#######################################################')
print('Processing Global student progression')


for student in students:
  continue
  print(f'-- student {student} --')
  courses = students[student]['courses']
  note_counter = 0
  global_prog = "0%"
  global_prog_acc = 0
  for course in courses:
    course_progression = students[student]['courses'][course]['course_progression']
    
    print(f'course progression ({course}):  {course_progression} --')
    parsed_note = course_progression
    parsed_note = parsed_note.strip().replace('%', '')
    parsed_note = parsed_note.replace(',', '.')
    parsed_note = float(parsed_note)
    print(f"parsed note as {parsed_note}")
    global_prog_acc += parsed_note
    note_counter += 1
   
    
  if((note_counter == 0) or (global_prog_acc == 0.0)):
    global_prog = "0%"
  else:
    print(f' attempting {global_prog_acc}/{note_counter} ')
    f_global_score = round(global_prog_acc / note_counter,2)
    
    # now reparse format...
    s_global_score = str(f_global_score)
    s_global_score = s_global_score.replace('.', ',')
    s_global_score = s_global_score+'%'
    global_prog = s_global_score
  students[student]['global_progression'] = global_prog
  print(f"got {global_prog} ")
#####################


jsonStudents = json.dumps(students, ensure_ascii=False)
#print(jsonStudents)


#output_path = '/tmp/umn-api-tests/out.json'
output_path = '/edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/umn_learner_data_api/data.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(students,f, ensure_ascii=False, indent=4)
print('#######################################################')


##for i,s in enumerate(students):
##    color = colors[i % len(colors)]  # cycle through colors
##    print(f"{color}",end='')
##    print(s)
##
##    print(f"{reset}",end='')





timestamp_work = time.time()

dif_query = timestamp_query-timestamp_begin
dif_work = timestamp_work-timestamp_query

timestamp_end = time.time()
dif_end = timestamp_end-timestamp_begin


timestamp_exit = time.time()
dif_global = timestamp_exit-timestamp_startup

print(f' query took {round(dif_query*1000,3)}ms / {str(int(dif_query))} secs')
print(f' work took {round(dif_work*1000,3)}ms / {str(int(dif_work))} secs')
print(f' Total took {round(dif_end*1000,3)}ms / {str(int(dif_end))} secs')
print(f' Whole program took {round(dif_global*1000,3)}ms / {str(int(dif_global))} secs')

#################
exit()


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/grade_reports_api/generate.py

