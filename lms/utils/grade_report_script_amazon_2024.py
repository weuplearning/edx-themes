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
import datetime
import json

# from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx import locator
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.courseware.courses import get_course_by_id

from lms.djangoapps.wul_apps.best_grade.helpers import check_best_grade

from common.djangoapps.student.models import User, UserProfile
# from lms.djangoapps.courseware.models import StudentModule
from student.models import CourseEnrollment


from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import logging
log = logging.getLogger()



emails = sys.argv[1].split(";")
course_ids = sys.argv[2].split(";")

## Workbook
wb = Workbook()
ws = wb.active
ws.title = "Grading report"


## Construct data
users = User.objects.all()
users_data = dict()
siret = dict()

# Headers
headers = ["Nombre", "Identificador público de usuario","Correo","Fecha de creación", "Fecha de la última conexión","Tiempo empleado","Número de cursos realizados","Número de cursos completados","Introducción a la venta en Amazon","Crea tu negocio","Los mejores consejos de los líderes de Amazon","Construye tu presencia y marca en Amazon","Fundamentos del marketing de contenidos","Logística y sostenibilidad","Comienza tu propia empresa de venta online","Venta online internacional","Primeros pasos en la venta online","Incrementa tu negocio con las ventas digitales","Principios para gestionar tu empresa","Operaciones comerciales, logística y métodos de envío","Liderazgo y estilos de gestión","Analiza tu base de clientes","Gestión financiera","Consideraciones financieras","Define tu estrategia de ventas","Exportación","Diseña un plan de crecimiento","Crear valor para tu negocio","Fundamentos de marketing","Estrategia de ventas online","Introducción a la financiación","Construye una marca",]



today = datetime.datetime.now(datetime.timezone.utc)



### Loop over all_user 


for index, user in enumerate(users):

    ## uncomment this lines for testing, 
    # if index == 250:
    #    break


    # Escape fake email address
    if user.email.find("@example")!= -1 or user.email.find("@fake")!= -1:
        continue
    # if user.email.find("@example")!= -1 or user.email.find("@themoocagency") != -1 or user.email.find("@weuplearning")!= -1 or user.email.find("@yopmail")!= -1 or user.email.find("@amazon")!= -1 or user.email.find("@fake")!= -1:
    #     continue


    user_data = dict()

    user_data["name"] = user.profile.name
    try:
        user_data["id"] = user.id
    except:
        user_data["id"] = ""
    try:
        user_data["username"] = user.username
    except:
        user_data["username"] = ""
    try:
        user_data["email"] = user.email
    except:
        user_data["email"] = ""

    custom_field = json.loads(user.profile.custom_field)
    try:
        user_data["date_joined"] = user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    except:
        user_data["date_joined"] = ""
    try:
        user_data["last_login"] = user.last_login.strftime('%Y-%m-%d %H:%M:%S')
    except:
        user_data["last_login"] = ""


    user_row = []
    video_dict = dict()
    user_data["enrolled_to"] = 0
    user_data["finished_course"] = 0
    user_data["total_video_views"] = 0


    ### Grade Data

    global_time_tracking_cumul = 0


    for course_id in course_ids :

        all_course_enrollment = CourseEnrollment.objects.filter(user=user)
        user_data[course_id] = ''


        for enrollment in all_course_enrollment :


            if str(course_id) == str(enrollment.course_id) :

                course_key = CourseLocator.from_string(course_id)
                course = get_course_by_id(course_key)

                user_data["enrolled_to"] += 1

                #log.info(course_id)
                try:
                    gradesTest = check_best_grade(user, course, force_best_grade=True)
                    user_data[course_id] = gradesTest.summary['percent']

                    if gradesTest.summary['percent'] >= 0.7 :
                        user_data["finished_course"] += 1
                except:
                    user_data[course_id] = 'Pas noté'


                try:
                    course_key = locator.CourseLocator.from_string(str(course_id))
                    wul_course_enrollment = WulCourseEnrollment.objects.get(course_enrollment_edx__user=user, course_enrollment_edx__course_id=course_key)

                    global_time_tracking = wul_course_enrollment.global_time_tracking
                    global_time_tracking_cumul += global_time_tracking
                except:
                    pass


    ### TimeTracking Data

    if global_time_tracking_cumul == 0 :
        user_data["global_time_tracking"] = 'n/a'
    else:
        user_data["global_time_tracking"] = datetime.timedelta(seconds=global_time_tracking_cumul)




    user_row = [user_data["name"],user_data["username"],user_data["email"],user_data["date_joined"],user_data["last_login"],user_data["global_time_tracking"],user_data["enrolled_to"],user_data["finished_course"]]
    # user_row = [user_data["username"],user_data["email"],user_data["name"],user_data["region"],user_data["siret"],user_data["phone_number"],user_data['online_sales'],user_data["date_joined"],user_data["last_login"],user_data["global_time_tracking"],user_data["enrolled_to"],user_data["finished_course"]]

    for course_id in course_ids :
        user_row.append(user_data[course_id])


    users_data[user.username.capitalize()] = user_row

ordered_users = sorted(users_data.items(), key=lambda x: x[1])


### Print excel file


row = 1

sheet = wb.active
for i, header in enumerate(headers):
    sheet.cell(1, (i+1), header)
    sheet.cell(1, i+1).fill = PatternFill("solid", fgColor="1E2631")
    sheet.cell(1, i+1).font = Font(b=True, color="BA4926")
j=2

for user in ordered_users:
    user_row = user[1]
    l=0
    for value in user_row :
        sheet.cell(row=j, column=(l+1)).value = value
        l=l+1
    j=j+1

timestr = time.strftime("%Y_%m_%d")
filename = "Amazon_ratings_report_{}.xlsx".format(timestr)
filepath = '/home/ubuntu/amazon_reports/{}'.format(filename)
wb.save(filepath)


### Create a new zip file and write the Excel file into it


zipname = "ratings_report.zip"
zippath = '/home/ubuntu/amazon_reports/{}'.format(zipname)

with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
    myzip.write(filepath, arcname=filename)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()
html = "<html><head></head><body><p>Hola,<br/><br/>Adjunto encontrará el informe de datos de Amazon<br/><br/>Buena bienvenida<br />The Weup Equipo de aprendizaje</html>"


### Send email


for email in emails:

    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "Amazon <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Amazon ratings report"

    attachment = _files_values

    # Load your zip file instead of the Excel file
    with open(zippath, 'rb') as f:
        attachment = f.read()
        
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= {}".format(zipname))
    msg.attach(part)

    server = smtplib.SMTP('mail3.themoocagency.com', 25)
    server.starttls()
    server.login('contact', 'waSwv6Eqer89')
    msg.attach(part2)
    text = msg.as_string()
    server.sendmail(fromaddr, email, text)
    server.quit()

    print('Email sent to ',email)


## delete old files
two_weeks_ago = datetime.datetime.today() - datetime.timedelta(days=14)
try:
    os.remove('/home/ubuntu/amazon_reports/Amazon_ratings_report_{}.xlsx'.format(two_weeks_ago.strftime("%Y_%m_%d")))
except:
    pass



#qualif
# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/amazon-espagne/lms/utils/grade_report_script_amazon_2024.py "cyril.adolf@weuplearning.com" "course-v1:amazon-espagne+test+2024"

# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/amazon-espagne/lms/utils/grade_report_script_amazon_2024.py "cyril.adolf@weuplearning.com" "course-v1:amazon-es+introduccion_a_la_venta+az_01;course-v1:amazon-es+crea_tu_negocio+az_02;course-v1:amazon-es+consejos_lideres_amazon+az_03;course-v1:amazon-es+construye_presencia_marca_amazon+az_04;course-v1:amazon-es+fundamentos_marketing_contenidos+az_05;course-v1:amazon-es+logistica_y_sostenibilidad+az_06;course-v1:amazon-es+comienza_empresa_venta_online+az_07;course-v1:amazon-es+venta_online_internacional+az_08;course-v1:amazon-es+primeros_pasos_venta_digital+az_09;course-v1:amazon-es+incrementa_negocio_ventas_digitales+az_10;course-v1:amazon-es+principios_gestionar_empresa+az_11;course-v1:amazon-es+operaciones_comerciales_logistica_envio+az_12;course-v1:amazon-es+liderazgo_estilos_gestion+az_13;course-v1:amazon-es+analiza_base_clientes+az_14;course-v1:amazon-es+gestion_financiera+az_15;course-v1:amazon-es+consideraciones_financieras+az_16;course-v1:amazon-es+define_estrategia_ventas+az_17;course-v1:amazon-es+exportacion+az_18;course-v1:amazon-es+plan_de_crecimiento+az_19;course-v1:amazon-es+crear_valor_negocio+az_20;course-v1:amazon-es+fundamentos_marketing+az_21;course-v1:amazon-es+estrategia_ventas_online+az_22;course-v1:amazon-es+introduccion_financiacion+az_23;course-v1:amazon-es+construye_marca+az_24"
