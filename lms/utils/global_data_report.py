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
from datetime import datetime, timedelta  # Importez en haut du fichier si pas déjà fait

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import logging
log = logging.getLogger()


emails_to_send = sys.argv[1].split(";")
course_ids = sys.argv[2].split(";")

line_to_write = []


for course_id in course_ids:

    headers_base = ["Cours", "Inscription total", "Inscription sur 30 jours"]
    sections_name_dict = {
        "course-v1:emploi-store+MOOC1+2022_T4" : ["Introduction (min.)","Identifier ses compétences (min.)","Quels sont mes intérêts professionnels ? (min.)", "La faisabilité du projet (min.)", "Définir ma stratégie professionnelle et mon plan d'action (min.)"],
        "course-v1:emploi-store+MOOC3+2022_T4" : ["Introduction (min.)","Construire le fond de son CV (min.)","Construire la structure de son CV (min.)","Adapter son CV en fonction du métier (min.)","Rédiger une lettre de motivation (min.)","Candidature en réponse à une offre (min.)","Candidature spontanée (min.)"],
        "course-v1:emploi-store+MOOC4+2022_T4" : ["Introduction (min.)","Qu'est-ce qu'un entretien d'embauche (min.)","Se préparer à l'entretien d'embauche (min.)","Passer l'entretien (min.)","L'après-entretien : relancer les recruteurs (min.)","Préparer son intégration à l'entreprise (min.)"],
        "course-v1:emploi-store+MOOC5+2022_T4" : ["Bienvenue (min.)","Séquence 1 (min.)","Séquence 2 (min.)","Séquence 3 (min.)","Séquence 4 (min.)","Questionnaire de satisfaction (min.)"],
    }
    headers = headers_base + sections_name_dict[course_id]

    line_to_write.append(headers)

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)
    course_name = course.display_name


    sections_course_dict = {
        "course-v1:emploi-store+MOOC1+2022_T4" : {
            "cd0db741c85b41058523d583811a9408" :0,
            "3c27eed2aa904317a599ab9d9dfa65f2" :0,
            "09dfede564a142d4a919749b77f00cce" :0,
            "f4df99e60b114719ad08c36523352255" :0,
            "5662abd3965c40af99c7e1a53c6e4763" :0
        },
        "course-v1:emploi-store+MOOC3+2022_T4" : {
            "b443d8fc4d4d4c66a3f692cee5cec47f" :0,
            "3e12dc50676f4b7dac6b3de57971e9c6" :0,
            "544cf4bed1724e0db17f75f6c29dcbf1" :0,
            "1b5728e5797443179663fcd6d42edb80" :0,
            "bdce23323e0e40c8a19164345a6772ea" :0,
            "f3ef32bc48fe46f592d1d5fe4ff915a6" :0,
            "1822654c250a4bd9a24b4b2e73daa392" :0
        },
        "course-v1:emploi-store+MOOC4+2022_T4" : {
            "0899c2c7473042ea89677ef9a0e5577f" :0,
            "caa88199176145d8820558d9641e9d3d" :0,
            "f6288a8dec7948cda57dc95d142179e4" :0,
            "f7bb828f5da844ccb83848aeaf2752d7" :0,
            "b42a0b6f99e346849d269f640b50d1d2" :0,
            "a328a113ae334730a28c4ac6978762f1" :0
        },
        "course-v1:emploi-store+MOOC5+2022_T4" : {
            "221d2332c76141b08c2aaaea8ca22e80" :0,
            "58dfc9e116b74781802cf11a6e8b39b3" :0,
            "e4b66510265f450b86c3e43e788fb153" :0,
            "07511b8c0cf840a8b3ba74f4f4d46e33" :0,
            "bbebe54b1a9e40c1ba464e769837995d" :0,
            "ea9cb465d0784081b07337fcb045417a" :0
        }
    }
    time_tracking_dict = sections_course_dict[course_id]
    
    course_data = []
    global_time_tracking = 0
    user_count_new = 0
    user_count_all = 0


    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        if user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 or user.email.find('@yopmail') != -1 :
           continue


        enroll_date = str(course_enrollments[i]).split('(')[1].split(' ')[0]
        enroll_dt = datetime.strptime(enroll_date, '%Y-%m-%d').date()
        date_limit = datetime.now().date() - timedelta(days=30)

        if enroll_dt < date_limit:
            user_count_all +=1
        else:
            user_count_all +=1
            user_count_new +=1


        try:
            wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)
            tt_detailled = wul_course_enrollment.detailed_time_tracking
            tt_detailled_dict = json.loads(tt_detailled)

            for key, value in tt_detailled_dict.items() :
                if key in time_tracking_dict.keys() :
                    time_tracking_dict[key] += value
        except:
            pass



    course_data.append(course_name)
    course_data.append(user_count_all)
    course_data.append(user_count_new)
    for section, time in time_tracking_dict.items() :
        minute = time//60
        course_data.append(round(minute/user_count_all,2))


    # donnée global pour un cours
    line_to_write.append(course_data)
    line_to_write.append("")


## Workbook
wb = Workbook() 
sheet = wb.active


l=1
for line in line_to_write:
    k=1
    for data in line :
        sheet.cell(row=l, column=k).value = data
        k+=1
    l+=1


filename = "grade_report_emploi_store.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note concernant la plateforme MOOC.emploi-store.fr<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport Mooc Emploi Store"

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



# sudo /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/emploi-store/lms/utils/global_data_report.py 'cyril.adolf@weuplearning.com' 'course-v1:emploi-store+MOOC1+2022_T4;course-v1:emploi-store+MOOC3+2022_T4;course-v1:emploi-store+MOOC4+2022_T4;course-v1:emploi-store+MOOC5+2022_T4'

# sudo /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/emploi-store/lms/global_data_report.py 'cyril.adolf@weuplearning.com' 'course-v1:emploi-store+MOOC1+2022_T4;course-v1:emploi-store+MOOC3+2022_T4;course-v1:emploi-store+MOOC4+2022_T4;course-v1:emploi-store+MOOC5+2022_T4'
