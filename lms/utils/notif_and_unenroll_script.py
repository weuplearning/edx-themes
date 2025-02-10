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
from student.models import User
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from openedx.core.djangoapps.site_configuration import helpers 
from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade


from openpyxl import Workbook
import json


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


from datetime import timedelta
from django.utils import timezone


import logging
log = logging.getLogger()



email_notification_gap = 3
email_notification_gap_2 = 14
limited_period_access = 40


# Envoyer le rapport aux admins HEC ?
emails_to_send = sys.argv[1].split(";")

all_treated_users_unenroll = []
all_treated_users_notif_14 = []
all_treated_users_notif_3 = []

now = timezone.now()

admin_list = [
    "andrew.funck@hec.edu",
    "m.ashraf@outlook.fr",
    "schultehec@gmail.com",
    "astebro@hec.fr",
    "mona.mensmann@wiso.uni-koeln.de",
    "naja.pape@insead.edu"
]

course_ids = [
    "course-v1:hec-pole-emploi+IP_1+2025",
    "course-v1:hec-pole-emploi+IP_2+2025",
    "course-v1:hec-pole-emploi+IP_3+2025",
    "course-v1:hec-pole-emploi+IP_4+2025",
    "course-v1:hec-pole-emploi+NEG_1+2025",
    "course-v1:hec-pole-emploi+NEG_2+2025",
    "course-v1:hec-pole-emploi+NEG_3+2025",
    "course-v1:hec-pole-emploi+NEG_4+2025",
    "course-v1:hec-pole-emploi+WEB_1+2025",
    "course-v1:hec-pole-emploi+WEB_2+2025",
    "course-v1:hec-pole-emploi+WEB_3+2025",
    "course-v1:hec-pole-emploi+WEB_4+2025",
]
# koa-qualif
# course_ids = [
#     "course-v1:hec-pole-emploi+12+2024"
# ]


for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course = get_course_by_id(course_key)

    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        enrollment = course_enrollments[i]

        if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 or user.email in admin_list :
           continue

        if not enrollment.is_active :
            # On a déjà désactivé cet utilisateur
            continue


        # Ca dépend de ce qui définit que le cours est terminé
        gradesTest = check_best_grade(user, course, force_best_grade=True)
        userPercentGrade = gradesTest.summary['percent']


        # SI LE COURS EST TERMINE ON PEUT DESINSCRIRE
        if userPercentGrade == 1 :
            all_treated_users_unenroll.append('******* finish course ******  '+user.email)
            enrollment.unenroll(user, course_id)

        try:
            detailed_time_tracking = json.loads(WulCourseEnrollment.get_enrollment(user=user, course_id=course_id).detailed_time_tracking)
        except : 
            detailed_time_tracking = 0


        # Check if the date_joined is old enough to be deleted
        # if (user.date_joined <= now - timedelta(days=limited_period_access) and userPercentGrade >= 0.7) :
        if user.date_joined <= now - timedelta(days=limited_period_access)  :
            all_treated_users_unenroll.append('******* unenroll 40 days ******  '+user.email)
            enrollment.unenroll(user, course_id)



        # Cet email sera envoyé automatiquement si les apprenants ne commencent pas leurs modules d'apprentissage dans les 72 heures suivant l'activation de leur compte, après leur inscription et la visualisation de la vidéo d'introduction
        elif (user.date_joined == now - timedelta(days=(email_notification_gap)) and detailed_time_tracking == 0) :

            try:

                html = '<html><head></head><body><h3 style="text-align: center; color: #004677; font-weight: bold;">Lancez-vous aujourd\'hui !</h3><p>Bonjour,<br/><br/>Nous sommes ravis de vous accueillir sur notre plateforme pédagogique ! Depuis votre inscription, votre place est réservée pour une expérience unique.<br/><br/>Le temps presse... L\'atelier n\'attend que vous pour démarrer ! <br/><br/>Préparez-vous à plonger dans un atelier abordant les compétences à développer pour mener à bien son projet. Au travers de regards croisés de professeurs et d’entrepreneurs, nous vous donnerons les clés pour muscler vos qualités d’entrepreneur. <p style="text-align: center;"><a href="https://hec-pole-emploi.weup.in/login" style="display: inline-block;padding: 10px 20px;font-size: 16px;color: white;background-color: #004677;text-decoration: none;border-radius: 5px;font-weight: bold;">Je démarre !</a></p><br/>Cordialement,<br/>L\'&eacute;quipe de recherche</p><img src="https://hec-pole-emploi.weup.in/media/microsites/hec-pole-emploi/logo-hec-paris.jpg" alt="Signature" style="width:145px;height:100px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "hec-pole-emploi <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "En route vers l’entrepreneuriat – on n'attend que vous !"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users_notif_3.append('******* ERROR EMAIL 1 ******  '+user.email)



        # Cet email sera envoyé automatiquement si les apprenants ont commencé leurs modules d'apprentissage mais ne les ont pas tous terminés dans les 14 jours suivant l'activation de leur compte.
        elif (user.date_joined <= now - timedelta(days=(email_notification_gap_2)) and userPercentGrade <= 0.7) :
        # elif (user.date_joined <= now - timedelta(days=(email_notification_gap_2)) and detailed_time_tracking != 0 and userPercentGrade <= 0.7) :

            try:

                html = '<html><head></head><body><h3 style="text-align: center; color: #004677; font-weight: bold;">Vous y êtes presque !</h3><p>Bonjour,<br/><br/>Voilà quelques jours que vous avez commencé notre atelier sur comment muscler vos qualités d’entrepreneur. Bravo !<br/><br/> <span style="font-weight: bold;" >Faites le point sur vos compétences entrepreneuriales pour mener à bien votre projet. </span> <br/><br/>Il ne vous reste plus qu’une semaine pour profiter de l\'atelier ! Après cette date, votre accès à la plateforme expirera pour permettre à de nouveaux participants de rejoindre l\'aventure. <br/><br/>Nous vous encourageons vivement à le finir pour en bénéficier pleinement. Vous y êtes presque ! <p style="text-align: center;"><a href="https://hec-pole-emploi.weup.in/login" style="display: inline-block;padding: 10px 20px;font-size: 16px;color: white;background-color: #004677;text-decoration: none;border-radius: 5px;font-weight: bold;">Je continue !</a></p><br/>Cordialement,<br/>L\'&eacute;quipe de recherche</p><img src="https://hec-pole-emploi.weup.in/media/microsites/hec-pole-emploi/logo-hec-paris.jpg" alt="Signature" style="width:145px;height:100px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "hec-pole-emploi <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "N’oubliez pas de finir votre atelier pour en tirer tous les bénéfices !"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users_notif_14.append('******* ERROR EMAIL 2 ******  '+user.email)


all_treated_users = all_treated_users_unenroll + all_treated_users_notif_3 + all_treated_users_notif_14  


## Workbook
wb = Workbook() 
sheet = wb.active

l=1
k=1
for user in all_treated_users:
    sheet.cell(row=l, column=k).value = user
    l=l+1
    if l > 1000 :
        k += 1
        l = 1


filename = "Rapport_deleted_users.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = '<html><head></head><body><h3>Rapport des Utilisateurs Supprimés</h3><p>Bonjour,<br/><br/>Voici la liste des '+str(len(all_treated_users_unenroll))+' utilisateurs désinscrit des cours HEC<br/>En cas de besoin vérifier le script : /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/delete_inactive_user_hec.py <br/>Bonne r&eacute;ception<br/>L\'&eacute;quipe WeUp Learning</p></body></html>'


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport deleted users"

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


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/notif_and_unenroll_script.py 'cyril.adolf@weuplearning.com'
