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
from student.models import CourseEnrollment
from student.models import User
from lms.djangoapps.wul_apps.models import WulCourseEnrollment


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



limited_period_access_1 = 366
limited_period_access_2 = 306
limited_period_access_3 = 31

one_month_notification_gap = 31


emails_to_send = sys.argv[1].split(";")

all_treated_users = []

now = timezone.now()

course_ids = [
    "course-v1:af-brasil+PP+2024",
    "course-v1:af-brasil+go+2024",
    "course-v1:af-brasil+go+degustation",
    "course-v1:af-brasil+OFM+01"
]

for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)

    for i in range(len(course_enrollments)):

        enrollment = course_enrollments[i]
        user = enrollment.user
        org = enrollment.course_overview.org

        # Ajouter les admins AF-Brasil
        if user.email.find('@weuplearning') != -1 or user.email.find('@themoocagency') != -1 or user.email.find('@fake.email') != -1 or user.email.find('@example.com') != -1 or user.email.find('@rioaliancafrancesa.com.br') != -1 or user.email.find('psgmrosa@gmail.com') != -1 or user.email.find('@aliancafrancesaonline') != -1 :
           continue

        # On a déjà désactivé cet utilisateur
        if not enrollment.is_active :
            continue

        # Vérifier si le cours est commencé
        try:
            detailed_time_tracking = json.loads(WulCourseEnrollment.get_enrollment(user=user, course_id=course_id).detailed_time_tracking)
        except : 
            detailed_time_tracking = 0

        # Inscrit depuis combien de jours 
        days_difference = (now - user.date_joined).days

        # can be delete after 10/03/2025
        if user.email.find('renatamonteiro1101@gmail.com') != -1 :
            days_difference -= 46


        # email_01
        if (((course_id == "course-v1:af-brasil+PP+2024" or course_id == "course-v1:af-brasil+OFM+01") and days_difference == (limited_period_access_1 - one_month_notification_gap)) or (course_id == "course-v1:af-brasil+go+2024" and days_difference == (limited_period_access_2 - one_month_notification_gap))) :

            all_treated_users.append('******* email J-30 PP+2024 ou OFM ou go+2024 ******  '+user.email)

            try : 
                html = '<html><head></head><body><p>Bonjour! 😊<br/><br/>Esperamos que você tenha aproveitado bastante o seu curso de francês até agora. Lembre-se de que seu acesso ao conteúdo estará disponível por mais 1 mês.<br/><br/>Aproveite este tempo para revisar, concluir atividades e liberar seu certificado! <br/>Estamos aqui para ajudar você nessa reta final se precisar! 🚀<br/><br/>Bonne continuation et à bientôt!<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        # email_02
        elif (course_id == "course-v1:af-brasil+PP+2024" and days_difference == (limited_period_access_1 - 1)) :


            all_treated_users.append('******* email J-1 PP+2024 ******  '+user.email)

            try : 
                html = '<html><head></head><body><p>Bonjour! 🎓<br/><br/>Hoje é o último dia do seu acesso ao seu curso de francês! <br/><br/>Esperamos que essa jornada tenha sido enriquecedora e cheia de aprendizado.<br/>Caso tenha interesse em continuar aprendendo, estaremos à disposição para novas aventuras linguísticas! 🤩<br/><br/>Merci et à très bientôt !<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        elif (course_id == "course-v1:af-brasil+PP+2024" and days_difference == (limited_period_access_1 )) :
            # E-mail envoyé hier, on peut unenroll
            all_treated_users.append('******* unenroll PP+2024 ******  '+user.email)
            enrollment.unenroll(user, course_id)



        # email_03_x
        elif ((course_id == "course-v1:af-brasil+go+2024" or course_id == "course-v1:af-brasil+OFM+01") and days_difference == (1)) :


            if course_id == "course-v1:af-brasil+go+2024" : 
                all_treated_users.append('******* email J+1 go+2024 ******  '+user.email)
                html = '<html><head></head><body><p><span style="font-weight: 700">Bienvenue dans ton cours On y va ! por Aliança Francesa.</span><br/><br/>Você está prestes a viver uma experiência apaixonante, cheia de aprendizado, cultura, emoção e diversão, na escola que é referência em ensinar francês e está presente há 140 anos em todo o mundo.<br/><br/>Nosso curso <span style="font-weight: 700">On y va ! Por Aliança Francesa</span> vai proporcionar uma imersão na língua francesa de uma maneira inovadora, com conteúdos digitais, vídeos, podcasts, exercícios interativos, desafios e medalhas a conquistar!<br/><br/>Com <span style="font-weight: 700">On y va ! Por Aliança Francesa</span> você tem o melhor do ensino on-line em autonomia, com 100% de flexibilidade e com a experiência histórica da Aliança Francesa!<br/><br/> <span style="font-weight: 700"> Desejamos a você um excelente curso e uma excelente experiência de aprendizado com On y va! por Aliança Francesa!</span><br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'
            else : 
                all_treated_users.append('******* email J+1 OFM ******  '+user.email)
                html = '<html><head></head><body><p><span style="font-weight: 700">Bienvenue dans ton cours Objectif Français Militaire niveau A1 (OFM A1) !</span><br/><br/>Você está prestes a viver uma experiência apaixonante e cheia de aprendizado na escola que é referência em ensinar francês e está presente há 140 anos em todo o mundo.<br/><br/>Nosso curso <span style="font-weight: 700">OFM A1</span> vai proporcionar uma imersão na língua francesa ! Aprenda a falar francês e impulsione sua carreira! Prepare-se para missões de paz em países francófonos. Desenvolva a comunicação no idioma em um curso criado com foco para militares das Forças Armadas do Brasil que possuem pouco ou nenhum conhecimento de francês.<br/><br/>Com <span style="font-weight: 700">OFM A1</span> você tem o melhor do ensino on-line em autonomia, com 100% de flexibilidade e com a experiência histórica da Aliança Francesa!<br/><br/><span style="font-weight: 700">Desejamos a você um excelente curso e uma excelente experiência de aprendizado com Objectif Français Militaire niveau A1!</span><br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'


            try : 
                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        # email_04_x
        elif ((course_id == "course-v1:af-brasil+go+2024" or course_id == "course-v1:af-brasil+OFM+01") and days_difference == (7) and detailed_time_tracking == 0) :


            if course_id == "course-v1:af-brasil+go+2024" : 
                all_treated_users.append('******* email J+7 go+2024 ******  '+user.email)
                html = '<html><head></head><body><p><span style="font-weight: 700">Bonjour !</span> <br/><br/>Percebemos que você ainda não começou seu curso online<span style="font-weight: 700"> On y va ! por Aliança Francesa.</span><br/><br/><span style="font-weight: 700">Quel dommage !</span> <br/><br/>Está tudo indo bem para você?<br/><br/>A equipe da Aliança Francesa Online está à disposição para responder a quaisquer perguntas que você possa ter.<br/><br/>Você pode entrar em contato com a Aliança Francesa onde comprou o “On y va! por Aliança Francesa” ou, no caso de um problema técnico, entrar em contato com <a href="mailto:faleconosco@aliancafrancesaonline.com.br">faleconosco@aliancafrancesaonline.com.br</a> <br/><br/>Esperamos vê-los ganhando as medalhas do curso <span style="font-weight: 700"> On y va ! por Aliança Francesa</span> muito em breve.<br/><br/>A très vite !<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'
            else : 
                all_treated_users.append('******* email J+7 OFM ******  '+user.email)
                html = '<html><head></head><body><p><span style="font-weight: 700">Bonjour !</span><br/><br/>Percebemos que você ainda não começou seu curso online <span style="font-weight: 700">Objectif Français Militaire niveau A1 (OFM A1).</span><br/><br/><span style="font-weight: 700">Quel dommage !</span> <br/><br/>Está tudo indo bem para você?<br/><br/>A equipe da Aliança Francesa Online está à disposição para responder a quaisquer perguntas que você possa ter.<br/><br/>Você pode entrar em contato com a Aliança Francesa onde comprou o <span style="font-weight: 700">Objectif Français Militaire niveau A1 (OFM A1) </span> ou, no caso de um problema técnico, entrar em contato com <a href="mailto:faleconosco@aliancafrancesaonline.com.br">faleconosco@aliancafrancesaonline.com.br</a> <br/><br/>Esperamos vê-los ganhando as medalhas do curso <span style="font-weight: 700">Objectif Français Militaire niveau A1 (OFM A1)</span> muito em breve.<br/><br/>A très vite !<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'


            try : 
                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        # email_05
        elif (course_id == "course-v1:af-brasil+go+2024" and days_difference == (limited_period_access_2 - 1)) :

            all_treated_users.append('******* email J-1 go+2024 ******  '+user.email)

            try : 
                html = '<html><head></head><body><p>Bonjour! 🎓<br/><br/>Hoje é seu último dia de acesso ao curso <span style="font-weight: 700">On y va ! por Aliança Francesa</span>, esperamos que essa jornada tenha sido enriquecedora e cheia de aprendizado.<br/><br/>Caso queira dar continuidade à sua jornada de aprendizado de francês, estaamos prontos a te apoiar na continuação de seu percurso linguístico! 🤩<br/><br/>Entre em contato com a Aliança Francesa mais próxima de sua residência ou nos procure em nossas redes sociais. Sabendo que, cada Aliança Francesa é única e as ofertas de cursos são individuais.<br/><br/>Merci et à très bientôt ! <br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        elif (course_id == "course-v1:af-brasil+go+2024"  and days_difference == (limited_period_access_2)) :
            # Unenroll here
            all_treated_users.append('******* unenroll go+2024 ******  '+user.email)
            enrollment.unenroll(user, course_id)



        # email_06
        elif (course_id == "course-v1:af-brasil+go+degustation" and days_difference == (1)) :

            all_treated_users.append('******* email J-1 degustation ******  '+user.email)

            try : 
                html = '<html><head></head><body><p>Bem-vinda.o ao nosso curso On y va ! por Aliança Francesa 🎉<br/><br/>Embarque em uma demonstração única de aprendizado de francês, com nosso curso 100% online e em autonomia para iniciantes! Uma experiência única pra você que já admira o cinema francês e quer começar aprender a língua ainda este ano.<br/><br/> ✨ Aprenda no Seu Ritmo: Flexibilidade total para se adequar à sua agenda lotada.<br/><br/>✨ Simples e Eficaz: Descomplicamos o francês para facilitar seu aprendizado desde o início e te proporcionando um aprendizado completo, para ser aplicado em situações do dia a dia, desde a primeira lição.<br/><br/>👉🏽 Nesta degustação <span style="font-weight: 700">você terá acesso à primeira lição de nosso curso On y va ! por Aliança Francesa</span> e poderá, então, começar seu aprendizado.<br/><br/>🎁 Este é um presente que temos a certeza que você vai gostar. Deguste o francês e comece essa jornada cultural com a gente.<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        # email_07_x
        elif ((course_id == "course-v1:af-brasil+go+degustation" and days_difference == (limited_period_access_3 - 1)) or (course_id == "course-v1:af-brasil+OFM+01" and days_difference == (limited_period_access_1 - 1))) :


            if course_id == "course-v1:af-brasil+go+degustation" : 
                all_treated_users.append('******* email J-1 degustation ******  '+user.email)
                html = '<html><head></head><body><p>Bonjour! 🎓 <br/><br/>Hoje é o último dia do seu acesso ao seu curso de francês <span style="font-weight: 700">Dégustation - On y va ! por Aliança Francesa.</span><br/><br/>Esperamos que essa jornada tenha sido enriquecedora e cheia de aprendizado. <br/><br/>Caso tenha interesse em continuar aprendendo, estaremos à disposição para novas aventuras linguísticas! 🤩<br/><br/>Use este link para continuar aprendendo com a Aliança Francesa Online: <a href="https://aliancafrancesaonline.com.br/">https://aliancafrancesaonline.com.br/</a> <br/><br/>Merci et à très bientôt !<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'
            else :
                all_treated_users.append('******* email J-1 OFM ******  '+user.email)
                html = '<html><head></head><body><p>Bonjour! 🎓 <br/><br/>Hoje é o último dia do seu acesso ao seu curso de francês <span style="font-weight: 700">Objectif Français Militaire niveau A1 (OFM A1).</span><br/><br/>Esperamos que essa jornada tenha sido enriquecedora e cheia de aprendizado. <br/><br/>Caso tenha interesse em continuar aprendendo, estaremos à disposição para novas aventuras linguísticas! 🤩<br/><br/>Use este link para continuar aprendendo com a Aliança Francesa Online: <a href="https://aliancafrancesaonline.com.br/">https://aliancafrancesaonline.com.br/</a> <br/><br/>Merci et à très bientôt !<br/><br/><span style="font-weight: 700">Aliança Francesa Online</span><br/></p><img src="https://cursos.aliancafrancesaonline.com.br/media/microsites/af-brazil/signature_afo.png" alt="Signature" style="width:245px;height:108px;"></body></html>'

            try : 

                part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
                fromaddr = "AF Online <ne-pas-repondre@themoocagency.com>"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = user.email
                msg['Subject'] = "Aliança Francesa"
                server = smtplib.SMTP('mail3.themoocagency.com', 25)
                server.starttls()
                server.login('contact', 'waSwv6Eqer89')
                msg.attach(part2)
                text = msg.as_string()
                server.sendmail(fromaddr, user.email, text)
                server.quit()
            except:
                all_treated_users.append('******* DEFAULT EMAIL ******  '+user.email)



        elif ((course_id == "course-v1:af-brasil+go+degustation" and days_difference == (limited_period_access_3) ) or (course_id == "course-v1:af-brasil+OFM+01" and days_difference == (limited_period_access_1)) ) :
            # Unenroll here
            all_treated_users.append('******* unenroll degustaion ou OFM ******  '+user.email)
            enrollment.unenroll(user, course_id)




if len(all_treated_users) == 0:
    stop




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

filename = "Rapport_notified_users.xlsx"
filepath = '/edx/var/edxapp/media/{}'.format(filename)
wb.save(filepath)

output = BytesIO()
wb.save(output)
_files_values = output.getvalue()

html = '<html><head></head><body><p>Bonjour,<br/><br/>Voici la liste des '+str(len(all_treated_users))+' utilisateurs notifiés et/ou désactivés.<br/><br/>En cas de besoin vérifier le script : /edx/app/edxapp/edx-themes/af-brazil/lms/utils/notif_and_unenroll_script.py <br/><br/>Bonne r&eacute;ception<br/>L\'&eacute;quipe WeUp Learning</p></body></html>'


for email in emails_to_send:
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "WeUp Learning <ne-pas-repondre@themoocagency.com>"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "Rapport notified users"

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


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/af-brazil/lms/utils/notif_and_unenroll_script.py 'cyril.adolf@weuplearning.com'
