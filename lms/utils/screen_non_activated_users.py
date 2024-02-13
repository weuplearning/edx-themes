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

from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from student.models import *
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from opaque_keys.edx.keys import CourseKey


from openpyxl import Workbook
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import logging
log = logging.getLogger(__name__)


# sys.setdefaultencoding('utf8')

timestr = time.strftime("%Y_%m_%d")
timesfr = time.strftime("%d.%m.%Y")
timesfr = str(timesfr)



_id = [
    "course-v1:afpa+LaPatisserie+MOOCPatisserieAFPA_S1", # colonne K
    "course-v1:afpa+LaPatisserie2+MOOCPatisserieAFPA_S2",
    "course-v1:afpa+MOOC_FLE_AFPA+FLE",
    "course-v1:afpa+Metsetvins+MOOCmetsetvinsAFPA_S3",
    "course-v1:afpa+Les101techniquesdebase+MOOCCUISINEAFPA",
    "course-v1:afpa+Les101techniquesdebase+MOOCCUISINEAFPA_S2",
    "course-v1:afpa+Les101techniquesdebase+MOOCCUISINEAFPA_S3",
    "course-v1:afpa+Les101techniquesreplay+2019",
    "course-v1:afpa+occitanie+2019_S1",
    "course-v1:afpa+MOOC_FLI+FLI_2019",
    "course-v1:afpa+La_Patisserie_Replay_2020+2020", # colonne U
    "course-v1:afpa+Mets_et_vins_replay_2020+2020",
    "course-v1:afpa+FLI+2023",
    "course-v1:afpa+replay_2020+2020",
    "course-v1:afpa+mixite+mixite_2020",
    "course-v1:afpa+CPF+CPF_2020",
    "course-v1:afpa+inclusion_sociale+2020", # colonne AA
    "course-v1:afpa+TRE_2020+2020",
    "course-v1:afpa+MATU+2020",
    "course-v1:afpa+love_food+2020",
    "course-v1:afpa+inclusion_sociale+2023" # colonne AE
]

domain_name_ok = [
    '@yopmail',
    '@example',
    '@orange.fr',
    '@gmail.com',
    '@live.fr',
    '@yahoo.fr', 
    '@yahoo.com',
    '@hotmail.fr',
    '@sfr.fr',
    '@laposte.fr',
    '@afpa.fr',
    '@wanadoo.fr',
    '@mail.ru',
    '@free.fr',
    '@laposte.net'
]



#PREPARE LE XLS

filename = '/edx/var/edxapp/media/microsites/afpa/reports_non_activated_afpa_users.xlsx'.format(timestr)
wb = Workbook()
sheet = wb.active
sheet.title= 'Enroll'


i = 1
for course_id in _id :

    course_key = CourseKey.from_string(course_id)
    enrollments = CourseEnrollment.objects.filter(course_id=course_key)

    for user in enrollments:
        user = user.user

        email = user.email.lower()
        suspect_email = False
        for domain in domain_name_ok :
            if email.find(domain) != -1 :
                suspect_email = True
        # if email.find('@yopmail') != -1 or email.find('@example') != -1 or email.find('@orange.fr') != -1 or email.find('@gmail.com') != -1 or email.find('@live.fr') != -1 or email.find('@yahoo.fr') != -1 or email.find('@hotmail.fr') != -1  :
        #     continue

        if suspect_email :
            continue        


        #if user.is_active :
        if user.last_login :
            continue 
        else :
            sheet.cell(i, 1, email)
        
        i = i+1






wb.close()
output = BytesIO()
wb.save(output)
_files_values = output.getvalue()


html = u"<html><head></head><body><p>Bonjour,<br/><br/>Voici la liste des inscrits Afpa.<br/><br/>Bonne reception<br>L'équipe WeUp Learning<br></p></body></html>"
part2 = MIMEText(html, 'html')
TO_EMAILS = sys.argv[1].split(";")

for i in range(len(TO_EMAILS)):
   fromaddr = "no-reply@themoocagency.com"
   toaddr = str(TO_EMAILS[i])
   msg = MIMEMultipart()
   msg['From'] = fromaddr
   msg['To'] = toaddr
   msg['Subject'] = "Inscriptions MOOC AFPA"
   attachment = _files_values
   part = MIMEBase('application', 'octet-stream')
   part.set_payload((attachment))
   encoders.encode_base64(part)
   part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(filename))
   msg.attach(part)
   server = smtplib.SMTP('mail3.themoocagency.com', 25)
   server.starttls()
   server.login('contact', 'waSwv6Eqer89')
   msg.attach(part2)
   text = msg.as_string()
   server.sendmail(fromaddr, toaddr, text)
   server.quit()
   print('mail send to '+str(TO_EMAILS[i]))




# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/afpa/lms/utils/screen_non_activated_users.py "cyril.adolf@weuplearning.com"



