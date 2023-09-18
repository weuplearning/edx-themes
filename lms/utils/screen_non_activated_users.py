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




#PREPARE LE XLS

filename = '/edx/var/edxapp/media/microsites/afpa/non_activated_users.xlsx'.format(timestr)
wb = Workbook()
sheet = wb.active
sheet.title= 'Enroll'


users = User.objects.all()

i = 1
for user in users:

    # log.info(user)
    # log.info(dir(user))
    # log.info(user.is_active)
    # log.info(user["is_active"])
    if user.email.find('@yopmail') != -1 :
        continue

    if user.is_active :
        continue 
    else :
        log.info(user.email)
        sheet.cell(i, 1,user.email)
    
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



