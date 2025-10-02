# -*- coding: utf-8 -*-
#!/usr/bin/env python
import importlib
import zipfile

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



import time
import json
import datetime

from opaque_keys.edx import locator

from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.courseware.courses import get_course_by_id
from student.models import CourseEnrollment

from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from common.djangoapps.student.models import User, UserProfile
from lms.djangoapps.courseware.models import StudentModule
from opaque_keys.edx.keys import UsageKey

# entry point to the block_structure api.
from openedx.core.djangoapps.content.block_structure.api import get_course_in_cache

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import logging
log = logging.getLogger()



try :
    emails = sys.argv[1].split(";")
except :
    emails = []


course_ids = [
    # "course-v1:hec-pole-emploi+WEB_1+2025",
    # "course-v1:hec-pole-emploi+IP_1+2025",
    # "course-v1:hec-pole-emploi+IP_2+2025",
    # "course-v1:hec-pole-emploi+IP_3+2025",
    # "course-v1:hec-pole-emploi+IP_4+2025",
    "course-v1:hec-pole-emploi+NEG_1+2025",
    # "course-v1:hec-pole-emploi+NEG_2+2025",
    # "course-v1:hec-pole-emploi+NEG_3+2025",
    # "course-v1:hec-pole-emploi+NEG_4+2025",
]


courses_structure = {
    # "course-v1:hec-pole-emploi+IP_1+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@113d642d6d224d4581107d552df0df1c": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+IP_2+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+IP_3+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+IP_4+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    "course-v1:hec-pole-emploi+NEG_1+2025" : [
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@7e4621359ba24e3d83a4fe54c71c47dd",

        # Session 1
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@685b7601be0d491ebead11f173957850",
        "espaceur car le bloc précédent contient 2 réponses",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@06b3b8fa36954ae29ae550895486fa73",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@01bc47db4ca041938955462ec6d490c5",
        # "block-v1:hec-pole-emploi+NEG_1+2025+type@conditional+block@7fedffd235634a7f8d3c493ac006d7da",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@scorm+block@825663373a73460bb0c7bc9f9feead19",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@4c27cb93579e411a9e62d4a8eebe9d08",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@6ce2c8d97115492eb18b2020a61afc85",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@478f768fde1c446d90620417879dca66",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@732b176b20a64dfb92bd61e4b203585a",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@0860e52e39c5425cb3a64c04edd38c57",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@c6a73372690a4ef3a4b05ac1e8d88b67",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@900d75ce7588400e98beb7025b12bae5",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@152c31e325b949f4b35c2dc4bd4c7407",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@3b696510868443fe824a38268c0894c5",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@problem+block@9de12455cd4f43f2b126d98685191f46",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@e6cbb477f25249eb8b92aba139a8745a",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@survey+block@cfca8207bff94103adfc2f7bb6beaa40",
        "espaceur",

        # Session 2
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@5a0e70d1eec94f4197f4c5b4459a4559",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@scorm+block@bc27da548b35437cb6988e887f797a6e",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@05e6336409e0486a8f736532e3ec41a4",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@f4fb777804544404ae6023fbef4c747b",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@9e7bf750d57242faa271a75c41a7efc5",

    ],
    # "course-v1:hec-pole-emploi+NEG_2+2025" : {
    #     "block-v1:hec-pole-emploi+NEG_2+2025+type@scorm+block@9f693653691f4b5daa0de77dd18d3e12": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+NEG_3+2025" : {
    #     "block-v1:hec-pole-emploi+NEG+2023+type@scorm+block@75d793663c1d4256aedd2ae063d3c978": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+NEG_4+2025" : {
    #     "block-v1:hec-pole-emploi+NEG+2023+type@scorm+block@75d793663c1d4256aedd2ae063d3c978": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+WEB_1+2025" : {},
    # "course-v1:hec-pole-emploi+WEB_2+2025" : {},
    # "course-v1:hec-pole-emploi+WEB_3+2025" : {},
    # "course-v1:hec-pole-emploi+WEB_4+2025": {}
}
key_dict ={
    "course-v1:hec-pole-emploi+NEG_1+2025" : [
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@7e4621359ba24e3d83a4fe54c71c47dd",
        "685b7601be0d491ebead11f173957850_3_1",
        "685b7601be0d491ebead11f173957850_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@06b3b8fa36954ae29ae550895486fa73",
        "01bc47db4ca041938955462ec6d490c5_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@4c27cb93579e411a9e62d4a8eebe9d08",
        "6ce2c8d97115492eb18b2020a61afc85_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@478f768fde1c446d90620417879dca66",
        "732b176b20a64dfb92bd61e4b203585a_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@0860e52e39c5425cb3a64c04edd38c57",
        "c6a73372690a4ef3a4b05ac1e8d88b67_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@900d75ce7588400e98beb7025b12bae5",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@152c31e325b949f4b35c2dc4bd4c7407",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@3b696510868443fe824a38268c0894c5",
        "9de12455cd4f43f2b126d98685191f46_2_1",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@e6cbb477f25249eb8b92aba139a8745a",
        "enjoy",
        "recommend",
        "learn",
        "1758925220212",
        "1758925284278",
        "1758925285193",
        "1758925286127",
        "1758925286960",
        "1758925288444",
        "1758925357444",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@5a0e70d1eec94f4197f4c5b4459a4559",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@05e6336409e0486a8f736532e3ec41a4",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@f4fb777804544404ae6023fbef4c747b",
        "block-v1:hec-pole-emploi+NEG_1+2025+type@video+block@9e7bf750d57242faa271a75c41a7efc5"
    ]


}








# all_courses_video_student_module = []

users_data = dict()
users_per_course = dict()
# list_chapters_name = dict()
all_user_set = set()
# list_of_student_scorms = list()
videos_list = list()





def course_name(course_id):
    if course_id.find('IP_') != -1 : 
        return "Initiative Personnelle (IP)"
    elif course_id.find('WEB_') != -1 :
        return "Webinaire (WEB)"
    else : 
        return "Négociation (NEG)"






for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)
    users_data = dict()

    for i in range(len(course_enrollments)):
        user = course_enrollments[i].user


        # Escape fake email address
        # if str(user.email).find('cyril.adolf@weuplearning.com')  == -1 :
        # if user.email.find("@example")!= -1 or user.email.find("@themoocagency") != -1 or user.email.find("@weuplearning")!= -1 or user.email.find("@yopmail")!= -1 or user.email.find("@fake")!= -1:
            # continue


        user_data = dict()

        user_data.update({
            "id": getattr(user, "id", ""),
            "username": getattr(user, "username", ""),
            "email": getattr(user, "email", ""),
            "date_joined": getattr(user, "date_joined", "").strftime('%Y-%m-%d %H:%M:%S') if getattr(user, "date_joined", None) else "",
            "last_login": getattr(user, "last_login", "").strftime('%Y-%m-%d %H:%M:%S') if getattr(user, "last_login", None) else "",
            "name": user.profile.name
        })


        user_row = []
        video_dict = dict()

        log.info('treating user :')
        log.info(user.email)

        course_key = locator.CourseLocator.from_string(str(course_id))
        collected_block_structure = get_course_in_cache(course_key)


        try : 
            user_problems = StudentModule.objects.filter(student=user, course_id__exact=course_id, module_type="problem").values('state','module_state_key')
            user_videos = StudentModule.objects.filter(student=user, course_id__exact=course_id, module_type="video").values('state','module_state_key')
            user_surveys = StudentModule.objects.filter(student=user, course_id__exact=course_id, module_type="survey").values('state','module_state_key')



            answer_dict = {}


            for unit in courses_structure[course_id] :

                log.info('unit')
                log.info(unit)

                if unit.find('problem') != -1 :

                    for user_problem in user_problems:

                        if str(user_problem['module_state_key']) != str(unit) :
                            continue

                        if 'student_answers' not in user_problem['state'] :
                            continue

                        log.info('user_problem')
                        log.info(user_problem['state'])
                        log.info(user_problem['module_state_key'])


                        json_state = json.loads(user_problem['state'])

                        log.info('user_problem student_answers')
                        log.info(json_state)


                        if isinstance(json_state['student_answers'] , dict) :
                            for key, value in json_state['student_answers'].items() :
                                log.info(key)
                                answer_dict[key] = str(value)
                            break


                        answer_dict[str(user_problem['module_state_key'])] = json_state['student_answers']
                        break







                if unit.find('video') != -1 :


                    for user_video in user_videos:
                        log.info('VIDEO UNIT')
                        log.info('VIDEO UNIT')
                        log.info(user_video)

                        if str(user_video['module_state_key']) != str(unit) :
                            continue


                        json_state = json.loads(user_video['state'])
                        log.info(json_state)

                        answer_dict[str(user_video['module_state_key'])] = json_state['saved_video_position']
                        break





                if unit.find('survey') != -1 :


                    for user_survey in user_surveys:
                        log.info('SURVEY UNIT')
                        log.info('SURVEY UNIT')
                        log.info(user_survey)

                        if str(user_survey['module_state_key']) != str(unit) :
                            continue

                        json_state = json.loads(user_survey['state'])
                        log.info("json_state survey here")
                        log.info(json_state)

                        if isinstance(json_state['choices'] , dict) :
                            for key, value in json_state['choices'].items() :
                                log.info(key)
                                answer_dict[key] = str(value)
                            break


                        answer_dict[str(user_survey['module_state_key'])] = json_state['completed']
                        break


                log.info('unit at the end of the loop')
                log.info(unit)
                # log.info(user_problem)
                # log.info(user_video)
                # log.info(user_survey)





        except : 
            log.info('no student module found')
            log.info('no student module found')
            log.info('no student module found')


        log.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ answer_dict')
        log.info(answer_dict)


        try:
            wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
            global_time_tracking = wul_course_enrollment.global_time_tracking
        except:
            global_time_tracking = 0

        user_data["global_time_tracking"] = datetime.timedelta(seconds=global_time_tracking)



        user_row = [user_data["username"],user_data["email"],user_data["name"],user_data["date_joined"],user_data["last_login"], user_data["global_time_tracking"]]

        for unit in key_dict[course_id] :
            if unit in answer_dict :
                user_row.append(answer_dict[unit])
            else :
                user_row.append('')


        log.info('user_row')
        log.info(user_row)

        users_data[user.username.capitalize()] = user_row
    users_per_course[course_id] = users_data




## Workbook
wb = Workbook()
wb.remove(wb.active)



def create_sheet_function(sheet_name, users, workbook):

    common_header = ["Username","Email","Nom complet","Date de création de compte","Date de dernière connexion","Temps passé total"] 

    questions_header = [
        "introduction - video", 

        # session 1
        "A votre avis 1/2", 
        "A votre avis 2/2", 
        "Le cas: Ancienne papeterie - video",
        "Le cas: Ancienne papeterie - checkbox",
        # "Simulation: Ancienne papeterie - scorm", 
        "La première offre - video", 
        "Quiz: La première offre?", 
        "Prix de réserve - video",
        "Prix de réserve - quiz",
        "Zone de négociation - video",
        "Zone de négociation - quiz",
        "Le biais du coût irrécupérable - video",
        "Q & R Le prix de réserve - video",
        "Le BATNA - video",
        "Le BATNA - quiz",
        "La conclusion - video",
        "La conclusion - survey 1/10",
        "La conclusion - survey 2/10",
        "La conclusion - survey 3/10",
        "La conclusion - survey 4/10",
        "La conclusion - survey 5/10",
        "La conclusion - survey 6/10",
        "La conclusion - survey 7/10",
        "La conclusion - survey 8/10",
        "La conclusion - survey 9/10",
        "La conclusion - survey 10/10",

        # session 2
        "Le cas : l'atelier - video",
        # scorm
        "L'ancrage - video",
        "Point d'aspiration - video",
        "Établir des relations - video"
    ]

    common_header = common_header + questions_header


    sheet = workbook.create_sheet(sheet_name)

    for i, header in enumerate(common_header):
        sheet.cell(row=1, column=(i+1)).value = header

    j=2
    for user in users:
        user_row = user[1]
        l=0
        for value in user_row :
            sheet.cell(row=j, column=(l+1)).value = value
            l=l+1
        j=j+1



for course_id in course_ids:
    users_data = users_per_course[course_id]
    if users_data == []:
        continue
    ordered_users = sorted(users_data.items(), key=lambda x: x[1])
    create_sheet_function(course_name(course_id), ordered_users, wb)



filename = "hec_grade_report.xlsx"
filepath = '/edx/var/edxapp/media/microsites/hec-pole-emploi/reports/{}'.format(filename)
wb.save(filepath)
output = BytesIO()
_files_values = output.getvalue()
html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de donn&eacute;es HEC France-Travail</p></body></html>"

## Send email
for email in emails:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "HEC France-Travail <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Data report HEC France-Travail"

    attachment = _files_values

    with open(filepath, 'rb') as f:
        attachment = f.read()

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

    log.info('Email sent to '+email)




# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/data_report_hec.py "cyril.adolf@weuplearning.com"


# September Test
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/data_report_hec_2.py "cyril.adolf@weuplearning.com"

