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



email_notification_gap = 7
email_notification_gap_bis = 14
limited_period_access = 32

# Envoyer le rapport aux admins HEC 
emails_to_send = sys.argv[1].split(";")

all_treated_users = []

now = timezone.now()


course_ids = [
    "course-v1:hec-pole-emploi+IP+2023",
    "course-v1:hec-pole-emploi+IP_NEG+2023",
    "course-v1:hec-pole-emploi+NEG+2023",
    "course-v1:hec-pole-emploi+webinaire+2023"
]
# koa-qualif
course_ids = [
    "course-v1:hec-pole-emploi+01+2022"
]


for course_id in course_ids:
    course_key = CourseLocator.from_string(course_id)
    course = get_course_by_id(course_key)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    course_name = course.display_name_with_default

    for i in range(len(course_enrollments)):

        user = course_enrollments[i].user
        enrollment = course_enrollments[i]

        # if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 :
        #    continue

        try :
            org = enrollment.course_overview.org
            platform_name = helpers.get_value_for_org(org, 'LMS_ROOT_URL')
        except :
            continue



        # Check if the date_joined is old enough to be deleted
        if (user.date_joined <= now - timedelta(days=limited_period_access)) :

            all_treated_users.append(user.email)
            log.info(course_enrollments[i])
            # log.info(dir(course_enrollments[i]))
            # Only delete if course is finished or if course not started
            # -> TimeTracking = 0 ?

            try:
                detailed_time_tracking = json.loads(WulCourseEnrollment.get_enrollment(user=user, course_id=course_id).detailed_time_tracking)

                log.info(detailed_time_tracking)
            except : 
                log.info('except TT')

            if len(detailed_time_tracking) == 0 : 
                log.info("pas de TT")
            # user.delete()
            # RAJOUTER UNE BOUCLE POUR SUPPRIMER LES PERSONNES QUI ONT TERMINÉES LE COURS ? 
            # RAJOUTER UNE BOUCLE POUR SUPPRIMER LES PERSONNES QUI ONT TERMINÉES LE COURS ? 
            # RAJOUTER UNE BOUCLE POUR SUPPRIMER LES PERSONNES QUI ONT TERMINÉES LE COURS ? 
            # Grade
            gradesTest = check_best_grade(user, course, force_best_grade=True)
            userPersentGrade = gradesTest.summary['percent']
            log.info('gradesTest')
            log.info(gradesTest)
            log.info(userPersentGrade)
            log.info('userPersentGrade')




        elif (user.date_joined == now - timedelta(days=(limited_period_access - email_notification_gap))) :



            try:
                # EN ATTENTE DE RETOUR CLIENT
                log.info('envoi du mail à :')
                log.info(user.email)
                continue
                html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous recevez cet e-mail car il ne vous reste plus que 7 jours pour terminer votre formation"+course_name+".<br/>Sans nouvelle connexion de votre part, <strong>votre compte sera supprimé dans 7 jours</strong>, conformément à nos politiques d'utilisation.<br/>Cliquez ici <a href='"+platform_name+"/login' >"+platform_name+"</a> pour conserver votre compte et suivre votre formation.<br/><br/><br/>Bonne r&eacute;ception,<br/>L'&eacute;quipe HEC - Pole-Emploi</p></body></html>"

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                try :
                    fromaddr = helpers.get_value_for_org(org, 'email_from_address')
                except: 
                    fromaddr = "ne-pas-repondre@themoocagency.com"

                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Notification avant suppression de votre compte "+ platform_name
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        elif (user.date_joined == now - timedelta(days=(limited_period_access - email_notification_gap_bis))) :




            try:
                # EN ATTENTE DE RETOUR CLIENT
                log.info('envoi du mail à :')
                log.info(user.email)
                continue

                # EN ATTENTE DE RETOUR CLIENT
                html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous recevez cet e-mail car il ne vous reste plus que 14 jours pour terminer votre formation"+course_name+".<br/>Sans nouvelle connexion de votre part, <strong>votre compte sera supprimé dans 14 jours</strong>, conformément à nos politiques d'utilisation.<br/>Cliquez ici <a href='"+platform_name+"/login' >"+platform_name+"</a> pour conserver votre compte et suivre votre formation.<br/><br/><br/>Bonne r&eacute;ception,<br/>L'&eacute;quipe HEC - Pole-Emploi</p></body></html>"

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                try :
                    fromaddr = helpers.get_value_for_org(org, 'email_from_address')
                except: 
                    fromaddr = "ne-pas-repondre@themoocagency.com"

                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Notification avant suppression de votre compte "+ platform_name
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)








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

html = "<html><head></head><body><p>Bonjour,<br/><br/>Voici la liste des "+str(len(all_treated_users)-1)+" utilisateurs supprimés de la base de données<br/>En cas de besoin vérifier le script : /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/delete_inactive_user_hec.py <br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"


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


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/hec-pole-emploi/lms/utils/delete_inactive_user_hec.py 'cyril.adolf@weuplearning.com'
