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
    "course-v1:hec-pole-emploi+IP_1+2025",
    # "course-v1:hec-pole-emploi+IP_2+2025",
    # "course-v1:hec-pole-emploi+IP_3+2025",
    # "course-v1:hec-pole-emploi+IP_4+2025",
    "course-v1:hec-pole-emploi+NEG_1+2025",
    "course-v1:hec-pole-emploi+NEG_2+2025",
    # "course-v1:hec-pole-emploi+NEG_3+2025",
    # "course-v1:hec-pole-emploi+NEG_4+2025",
]


scorm_page_ids = {
    "course-v1:hec-pole-emploi+temoin+2025" : { },
    "course-v1:hec-pole-emploi+IP_1+2025" : {
        "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@113d642d6d224d4581107d552df0df1c": "Scorm module"
    },
    # "course-v1:hec-pole-emploi+IP_2+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+IP_3+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    # "course-v1:hec-pole-emploi+IP_4+2025" : {
    #     "block-v1:hec-pole-emploi+IP_1+2025+type@scorm+block@76f94648789249ae8be25ee7b6b5e61d": "Scorm module"
    # },
    "course-v1:hec-pole-emploi+NEG_1+2025" : {
        "block-v1:hec-pole-emploi+NEG_1+2025+type@scorm+block@75d793663c1d4256aedd2ae063d3c978": "Scorm module"
    },
    "course-v1:hec-pole-emploi+NEG_2+2025" : {
        "block-v1:hec-pole-emploi+NEG_2+2025+type@scorm+block@9f693653691f4b5daa0de77dd18d3e12": "Scorm module"
    },
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



def scorm_data_treatment(suspend_data):

    listed_data = suspend_data.replace('3400','').replace('6000','&&').replace('^41000','&&').replace('r70020181^h_default_Selected','&&').split('&&')
    listed_data = list(filter(None, listed_data))
    log.info(listed_data)

    return listed_data





for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)
    users_data = dict()

    for i in range(len(course_enrollments)):
        user = course_enrollments[i].user


        # Escape fake email address
        if user.email.find("@example")!= -1 or user.email.find("@themoocagency") != -1 or user.email.find("@weuplearning")!= -1 or user.email.find("@yopmail")!= -1 or user.email.find("@fake")!= -1:
            continue

        user_data = dict()

        user_data.update({
            "id": getattr(user, "id", ""),
            "username": getattr(user, "username", ""),
            "email": getattr(user, "email", ""),
            "date_joined": getattr(user, "date_joined", "").strftime('%Y-%m-%d %H:%M:%S') if getattr(user, "date_joined", None) else "",
            "last_login": getattr(user, "last_login", "").strftime('%Y-%m-%d %H:%M:%S') if getattr(user, "last_login", None) else "",
            "name": user.profile.name
        })

        log.info('user_data')
        log.info(user_data)


        user_row = []
        video_dict = dict()
        user_data["total_video_time"] = datetime.timedelta(seconds=0)

        log.info('treating user :')
        log.info(user.email)

        course_key = locator.CourseLocator.from_string(str(course_id))
        collected_block_structure = get_course_in_cache(course_key)
        
        try : 
            user_scorms = StudentModule.objects.filter(student=user, course_id__exact=course_id, module_type="scorm").values("student_id", "module_state_key", "state")
            scorm_state = json.loads(user_scorms[0].get('state'))

            log.info('scorm_state')
            log.info(scorm_state)
            log.info(scorm_state["scorm_data"])

            user_data["grade"] = scorm_state["lesson_status"]

            try :
                user_data["scorm_time"] = scorm_state["scorm_data"]["cmi.interactions.0.timestamp"]
            except: 
                user_data["scorm_time"] = 'n.a.'

            try :
                user_data["raw_scorm_data"] = (scorm_state["scorm_data"]["cmi.suspend_data"])
                user_data["scorm_data"] = scorm_data_treatment(scorm_state["scorm_data"]["cmi.suspend_data"])
            except:
                user_data["scorm_time"] = 'n.a.'
                user_data["raw_scorm_data"] = 'n.a.'
                user_data["scorm_data"] = 'n.a.'

        except : 
            user_data["grade"] = 'n.a.'
            user_data["scorm_time"] = 'n.a.'
            user_data["raw_scorm_data"] = 'n.a.'
            user_data["scorm_data"] = 'n.a.'


        # Access TimeTracking for every courses
        global_time_tracking_cumul = 0

        try:
            detailed_time_tracking = json.loads(WulCourseEnrollment.get_enrollment(user=user, course_id=course_id).detailed_time_tracking)
            #keys = set(scorm_page_ids).intersection(detailed_time_tracking)
            #user_detailed_time_tracking = {k:detailed_time_tracking[k] for k in keys}

            user_detailed_time_tracking = {key: detailed_time_tracking[key] for key in scorm_page_ids if key in detailed_time_tracking}

            if user_detailed_time_tracking:
                total_time = user_detailed_time_tracking.values()
                user_data["scorm_time_tracking"] = datetime.timedelta(seconds=sum(total_time))
            else:
                user_data["scorm_time_tracking"] = datetime.timedelta(seconds=0)

        except:
            user_data["scorm_time_tracking"] = datetime.timedelta(seconds=0)

        try:
            wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
            global_time_tracking = wul_course_enrollment.global_time_tracking
            global_time_tracking_cumul += global_time_tracking

        except:
            pass

        user_data["global_time_tracking"] = datetime.timedelta(seconds=global_time_tracking_cumul)



        user_row = [user_data["username"],user_data["email"],user_data["name"],user_data["date_joined"],user_data["last_login"], user_data["global_time_tracking"], "N/A", user_data["total_video_time"], user_data["grade"]]
        # user_row = [user_data["username"],user_data["email"],user_data["name"],user_data["date_joined"],user_data["last_login"], user_data["global_time_tracking"], "N/A", user_data["total_video_time"], user_data["grade"], user_data["scorm_time"], user_data["raw_scorm_data"]]


        users_data[user.username.capitalize()] = user_row
    users_per_course[course_id] = users_data




## Workbook
wb = Workbook()
wb.remove(wb.active)



def create_sheet_function(sheet_name, users, workbook):

    common_header = ["Username","Email","Nom complet","Date de création de compte","Date de dernière connexion","Temps passé total","Cours finalisé","Temps passé","Note obtenue"] 
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
    msg['Subject'] = "Rapport temps passé HEC France-Travail"

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

