import os
from io import BytesIO
import json
import time

from opaque_keys.edx.locator import CourseLocator
from common.djangoapps.student.models import CourseEnrollment
from courseware.courses import get_course_by_id

from lms.djangoapps.courseware.models import StudentModule
from lms.djangoapps.grades.context import grading_context_for_course
from lms.djangoapps.grades.api import (
    CourseGradeFactory,
    context as grades_context,
    prefetch_course_and_subsection_grades,
)
from lms.djangoapps.courseware.user_state_client import DjangoXBlockUserStateClient



from completion.models import BlockCompletion


from openpyxl import Workbook

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import logging
log = logging.getLogger()


# Can not manage to pass var as arguments in command line
# course_ids = ['course-v1:bmd+test1609+2021']
course_ids = ['course-v1:bmd+FR+2022_02_9-10']
emails =['cyril.adolf@weuplearning.com']

block_id_dict = {
    'section_1': ['b8977b0d23b8451988f67810261cbaf4' ,'6abb25115bcc4ceabd920f42f02f911f', '6d477a377a39499da862232c088d1dd5', 'c3221290e0364e8ebc5a0d26ae274c7b', '175de0b46307493f9784e6d4c0227151', 'cf1dffbafe0e4336bc355b5f5064f514', '609840a6d3be4f489bda27df430d0f40', '6b76c1c82b9446ab812fc95c7b3a2f17', '5118756264874da5a854517357242cbf', '276dfbc7995e4c57810807d4cdc2f604', 'c34577726ffb4713ba13116bab0cb8c8' , '9562f9c2ee994be9bdd09d68ff1600ee', 'a3c2f665113745c3a39439f03360e6d3', '552419bae4d24fd98281628aa81280e1', '8125a2d6716d48108b0a695a64d662d6', 'c6ad12e09c734fcab7a55b5cdcf08304', 'afe0c87008da425d8837c1d7b565b0af', '2ace542ac2734e2c99aa195f293e1c2e', '60e5c2c3be104dacb36bfbaaafb269bc', '09537da71d1043a19bb8afa8a6e22476', '34ac173f97e840abb126f4b7f34a1579'],
    'section_2': ['d5ee1dc882d24bdb81c4c788c50e35b9', 'e8c3ddb56659414fb22599bc2992fc82'],
    'section_3': ['7e3c1e62c66e40deba9965ce99bf3285', '851fa1f40c524c999e436d5cc5564195', 'f284429ed3104774ab5fc5cccb545fba', '33c5e98a754e42a5b7125ce37379dd35', 'f0f24c498381431cb666212462dba95e', 'fdbc23846d67473288ffc8d794f0f39a', 'e7c6890f6845492d812d6e3ecaa3061d'],
    'section_4': ['a1d1bb2266714c4288a4f28763e2557a', 'b46018c8ec054b7a8b1bbcdec8457c5f', 'd806976ad7024118b09c0c0a55c483ab', '50351b5977294d3298b75b034e37bee4', 'be542f6da88247baac812699d69b058d', '2082ce18e8564dc783ec02266ebdfe69', '2d295b138d57452f9bd0685b15d0e040', '0b95f04af2ab4d76b7514e140e2d60b6', '825e6ed9d6084539871b130509dbee71', '4157e8120b904db6969529f124aff668', '5ac00a4881c945f3b1b3b2aa20aca834', 'a080c87f6b9c4c84860095c83b50f66a', 'b32e955ac82c4ec3b159ada6b74b5fe2', '8d5451adce1a4b2883623e13ae3470e6', '9dabd516af38463a89adac7946cdb51d', '8742cec7465c4bedaf4e1f21acda203b', '7f7a0215c835403aac83351fe17990e6', 'c1df8d04fcbb499a8f2f63651fd54f9b', '8eec1b1fd20e497bbe21a6df928e679c', '4bc2baedba594231a01dd87aa9b2c51c', '43bf2af1981f432d9b5df43e6b3edd14', '76fc61283d8446b79d5f06dafacb3266', '497eb759b4554f5292d11ce76fb3d862', '9d52880e911d4c5d8fe56b8a0c04798a'],
    'virtual_class_1': [],
    'section_6': ['d6f9f7457f7640daba223a43655e69a3', 'a5ec531c97b3412898feb5eeb882e62a', '203f241fe72d49fab784ff6bd37d07a0', 'd8cf1e113e6742e692e6cc0bbe0363df', '6cb2bc5b6a6b40eebf02cbcf7e2a19d9', '7a93a28411874834a57504defe5ade11', '11fb98e15a184628b75390a5e7c84e82'],
    'section_7': ['632cd05b4968489ba2c97def2b2355c6', '7b5411f0c1554cb8b155eb92e2e5a0da', 'ca78ed1ab53140f39c664900e4ad4fbb', 'c659c94cdc104c138019f6682fd5f6a1', 'f5e6c2707d804c85a2c1424ac095d824', '9156944eb362449598bd24d4847beb7b', '6493b71be5004a8bb73ee436518a0143', '82b3413e287d4cb48ef03aef79cba06c'],
    'virtual_class_2': [],
    'section_9': ['15fd353d7c69424299cea7f1e56ed3a7', '2f855dc6b98240f7af0da14722a27187', 'acd8ea431c9342979b50a920013742d7', 'd38f6ca1a4884fb189468c554f3c152d', '2961fc5fe1ff49139cfce7874179f8d4', 'ad73a16e89584fe7bff6920217876280'],
    'section_10': ['7e1084d6acaa41b7a588cafc53c597ad', '569193fbaf154d2f9273ea5c1755cbe1', '1f84aee5c0994641ad9b18db0d949cef', '1d564771a52f4ff092723c3849798f1d', '52b06874f66043f88a39b68288f4da08', '37d893b231ea4259a56542ec450ec873', '13cacb8243e943688a536b086c10a844', '7de7488b8eb5410dbc03d48d784649da', '9ee65dbfd78c49abadcc7102a3af003c', 'eed1816bda854578bef8317161e343df', '181c8758c93444d4a9a31c6c2688c556', 'cf7738b4d7bc465ca9ed194018cb5b6b', 'd919a9d575d14be981cdf4a94f60f4d5', '65695548400747c9890b5d6150dc64f3', 'e6a39b736bc04e97938594f74fcfe723', '17e72f101d0648c4b2761ba363274fad', 'aeb706aa01f24210aee43f7a8461dc59', '7c7e3ff1dfd14bbcaea8101075031047', 'ea872f4dfe514b9aa347baea8b09f619', 'ab2cffdd73c84665ba0e752b7bfd1493', '51c48dfea377424c81cadcce75e432e8', 'f44d453b90d24c0ea12ab72f1ca57754', '385ef2f2548744049b235d834056a1f1', '6b19aa3cf21a44dc94306c771c29ed3c', 'a4fcb31fe1474b9186a6a1ba17dc438a', 'd1f21af087f44b379788b1d2400cc5e2', '13e1ea4e679c4055a17b70a0e247d38e', '98db593b38d244c6ab72d47ffc3ba184', '838df49cfe13439fb2aeb1fa6c33b7b5', '8fcf7cb6914b41b09cce4a137089ce46'],
    'virtual_class_3': [],
    'section_12': ['f83f87c4a111463883174e5a17055db4', 'd6f713b43e4e4ff591b9b83b0bcd2b1b', 'ba3bc242b64f4da391487390454ba588', '7ad57fc1d87d44eeb45f7093bb2e6411', '8d5a49e2d5ba4065a98710538f734294', 'a124614e7461458d9483f50259a00134'],
    'section_13': ['e48fa4ce34b7483cbc697ee63b885ffe'],
    'section_14': ['c7053bb878464c6080c67bc7cc3ffa23'],
    'section_15': [ '8a0b629305c0466eb9c53ba19966f31c', 'da6df173ca6547a0833e852afee0c0f1', '7ba9710a56de48e78964fd0928497228', 'bc6e5b0487454c50af6ece8bbc98ae54', '54fcfe20fcaf47f388985698796fd0cd', 'c5fcd183a1864b1fa34cf2f95f383d99', 'a0c33b4678fb46ff8b72d6eca17b4317', 'a7dba79c8cb14628802334b95d194927', '15411ca3ef9240a3802658de588a5afb', '4ffc1630a89449338dfd9aae25d83abc', 'f932c9224cde4286ab4a384cd51f4ce6', 'ed6db69e6ddb4d2d9f8e29d8a8f37b22', '4990a1dafde24087a07f40b4314dd001', '3bcd7e69181b4253af8aedff762abbe2', 'df650f3d88ef464f9c69ca239a921d18', 'e8f2e99c507449d3baeddad5b4b42e32', 'e8a9333fab5246e49d48c20e0da14572', '7dc52151cd0445a585f5a60c27a483e0', 'f52d83a4886944faa38461202a3c2139', '9d41814e4bf04688919f32dac6445966', 'f3a4be4fef894e20a05bc96bb6d95ffa', 'e05b76e38e9745fe80e526a6ce827e75', 'bd84fdbbc61343a29cf199af0f08652e', '4355840a5a3e4f21930f9a34f7473320', '04d7e4480d074b25a2fd9449e989e7a8', 'dcf7d558e9c74532be09842fb1af5537', '84e1ae3f897e472ca1fa9074482cf1c9', '68fd383cdef94ff59de4d22f8b27a6c9', '6839a56658e44b19a91f034fb000a980', '0dbde8bf55d2452b9be649d99ba9b4e0', 'df9d08db3f354c7a8d6590ab14f2942a', 'f0ef5e963c8e498e90f2d7e271f6c8cc', '9b65d95682314948b057b64d2c332ec7', 'e3ab16e7ff7c4a9499c131a62f97e0f4']
}

all_users_data = {}
log.info('------------> Begin fetching user data and answers')

at_least_one_student = False
course_names = []
course_names_html = []
completed_block = []


for course_id in course_ids:

    course_key = CourseLocator.from_string(course_id)
    course = get_course_by_id(course_key)
    course_names.append(course.display_name_with_default)
    course_names_html.append("<li>"+ str(course.display_name_with_default)+"</li>")

    course_data = {}

    course_enrollments = CourseEnrollment.objects.filter(course_id=course_key)
    # list_of_student_modules = StudentModule.objects.filter(course_id=course_key)

    # for user in (list_of_student_modules):
    for i in range(len(course_enrollments)):
        user = course_enrollments[i].user

        # session
        session = course_id.split('+')[1]
        log.info('-----> session: '+ str(session))

        user_data = {}

        course_block_completions = BlockCompletion.get_learning_context_completions(user, course_key)

        for e, value in course_block_completions.items():
            completed_block.append(e.block_id)

        at_least_one_student = True
        user_data["session"] = session

        try:
            user_data["email"] = user.email
        except:
            try:
                user_data["email"] = json.loads(user.profile.custom_field)['email']
            except:
                user_data["email"] = 'n.a.'

        try:
            user_data["firstname"] = user.first_name.capitalize()
        except:
            try:
                user_data["firstname"] = json.loads(user.profile.custom_field)['first_name'].capitalize()
            except:
                user_data["firstname"] = 'n.a.'

        try:
            user_data["lastname"] = user.last_name.capitalize()
        except:
            try:
                user_data["lastname"] = json.loads(user.profile.custom_field)['last_name'].capitalize()
            except:
                user_data["lastname"] = 'n.a.'

        try:
            user_data["virtual_class_1"] = json.loads(user.profile.custom_field)['virtual_class_1']
        except:
            user_data["virtual_class_1"] = False

        try:
            user_data["virtual_class_2"] = json.loads(user.profile.custom_field)['virtual_class_2']
        except:
            user_data["virtual_class_2"] = False

        try:
            user_data["virtual_class_3"] = json.loads(user.profile.custom_field)['virtual_class_3']
        except:
            user_data["virtual_class_3"] = False

        total_earned = 0
        total_possible = 0

        # # Access Section
        scorable_block_titles = []
        grading_context = grading_context_for_course(course)
        user_state_client = DjangoXBlockUserStateClient()
        list_question = []
        log.info(grading_context['all_graded_subsections_by_type'])
        for section in grading_context['all_graded_subsections_by_type']['Auto evaluation']:
            for unit in section['scored_descendants']:
                scorable_block_titles.append((unit.location))

        for block_location in scorable_block_titles:

            question = {}
            try:
                history_entries = list(user_state_client.get_history(user.username, block_location))
            except: 
                question['choice'] = 'n.a.'
                question['correctedGrade'] = 0
                question['time'] = 'n.a.'
                question['score'] = 'n.a.'
                user_data["grade"] = 'n.a.'
                continue

            problemNum = str(block_location)[-2:]
            question['problem'] = problemNum
            choices = []
            

            log.info('history_entries[0].state')
            log.info(history_entries[0].state)
            log.info(history_entries[0].state['score']['raw_earned'])
            log.info(history_entries[0].state['score']['raw_possible'])

            total_earned += history_entries[0].state['score']['raw_earned']
            total_possible += history_entries[0].state['score']['raw_possible']

            log.info("----------------------")


            # if len(history_entries[0].state) ==3:
            #     question['choice'] = 'n.a.'
            # else:
            #     for key, value in history_entries[0].state['student_answers'].items():
            #         choices = value
            #         question['choice'] = value

            # # GRADE NEED TO BE RECALCULATE DUE TO BVT SCALE
            # try:
            #     question['correctedGrade'] = updateGrade( problemNum, choices, answer_list)
            # except:
            #     question['correctedGrade'] = 0

            # try:
            #     question['time'] = history_entries[0].state['last_submission_time']
            # except:
            #     question['time'] = 'n.a.'

            # try:
            #     question['score'] = history_entries[0].state['score']['raw_earned']
            # except:
            #     question['score'] = 'n.a.'

            # list_question.append(question)




        log.info('grading_context')
        log.info(grading_context['all_graded_subsections_by_type']['Auto evaluation'])
        for unit in grading_context['all_graded_subsections_by_type']['Auto evaluation']:
            log.info(unit.values)
            log.info(unit.items)
            log.info(unit.keys)
            log.info(dir(unit))

        # for section in grading_context['all_graded_subsections_by_type']['Auto evaluation']:
        #     for unit in section['scored_descendants']:
        #         # log.info('unit')
        #         # log.info(unit)
        #         scorable_block_titles.append((unit.location))

        # for block_location in scorable_block_titles:

        #     question = {}
        #     try:
        #         history_entries = list(user_state_client.get_history(user.username, block_location))
        #     except: 
        #         question['choice'] = 'n.a.'
        #         question['correctedGrade'] = 0
        #         question['time'] = 'n.a.'
        #         question['score'] = 'n.a.'
        #         continue

        #     problemNum = str(block_location)[-2:]
        #     question['problem'] = problemNum
        #     choices = []
            

        #     if len(history_entries[0].state) ==3:
        #         question['choice'] = 'n.a.'
        #     else:
        #         for key, value in history_entries[0].state['student_answers'].items():
        #             choices = value
        #             question['choice'] = value

        #     question['correctedGrade'] = 0

        #     try:
        #         question['time'] = history_entries[0].state['last_submission_time']
        #     except:
        #         question['time'] = 'n.a.'

        #     try:
        #         question['score'] = history_entries[0].state['score']['raw_earned']
        #     except:
        #         question['score'] = 'n.a.'

        #     list_question.append(question)
        grade = total_earned / total_possible

        user_data["grade"] = round(grade, 2) *100

        data = { "general": user_data }
        # data = { "general": user_data, 'list_question' : list_question }
        course_data[str(user.id)]= data
        all_users_data[course_id]= course_data

log.info('------------> Finish fetching user data and answers')

log.info('------------> Begin Calculate grades and write xlsx report')

# WRITE XLS
timestr = time.strftime("%Y_%m_%d")
wb = Workbook()
sheet = wb.active
sheet.title= 'Rapport'
filename = '/home/edxtma/csv/{}_BMD_grade_report.xls'.format(timestr)

headers = ['Adresse e-mail', 'Prénom', 'Nom', 'Session','Note (%)', 'Chapitre 1', 'Chapitre 2', 'Chapitre 3', 'Chapitre 4', 'Chapitre 5', 'Chapitre 6', 'Chapitre 7', 'Chapitre 8', 'Chapitre 9', 'Chapitre 10', 'Chapitre 11', 'Chapitre 12', 'Chapitre 13', 'Chapitre 14', 'Chapitre 15' ]
first = True

for i, header in enumerate(headers):
    sheet.cell(1, i+1, header)
j=2
for k, course_id in all_users_data.items():
    for key, user in course_id.items():
        sheet.cell(j, 1, user['general']['email'])
        sheet.cell(j, 2, user['general']['firstname'])
        sheet.cell(j, 3, user['general']['lastname'])
        # Session
        sheet.cell(j, 4, user['general']['session'])
        sheet.cell(j, 5, user['general']['grade'])
        sheet.cell(j, 10, int(1)) if user['general']['virtual_class_1'] else sheet.cell(j, 10, int(0)) 
        sheet.cell(j, 13, int(1)) if user['general']['virtual_class_2'] else sheet.cell(j, 13, int(0)) 
        sheet.cell(j, 16, int(1)) if user['general']['virtual_class_3'] else sheet.cell(j, 16, int(0)) 
        

        correctedExamGrade = 0
        i = 5 
        for section, units in block_id_dict.items(): 
            completion = 0
            block_in_section = 0

            for unit in units :
                block_in_section += 1 

                if unit in completed_block : 
                    completion += 1

            if block_in_section != 0:
                ratio = round(completion/block_in_section, 2)
                sheet.cell(j, i+1, ratio)
            i += 1
            
    j += 1


# SEND MAILS
output = BytesIO()
wb.save(output)
_files_values = output.getvalue()
course_names_html = ''.join(course_names_html)

html = "<html><head></head><body><p>Bonjour,<br/><br/>Vous trouverez en pièce jointe le rapport de note : "+ course_names_html +"<br/><br/>Bonne r&eacute;ception<br/>L'&eacute;quipe WeUp Learning</p></body></html>"

for email in emails:
    if not at_least_one_student :
        log.info('at_least_one_student')
        log.info(at_least_one_student)
        break

    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    fromaddr = "ne-pas-repondre@themoocagency.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = email
    msg['Subject'] = "BMD_grade_report"
    attachment = _files_values
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(filename))
    msg.attach(part)
    server = smtplib.SMTP('mail3.themoocagency.com', 25)
    server.starttls()
    server.login('contact', 'waSwv6Eqer89')
    msg.attach(part2)
    text = msg.as_string()
    server.sendmail(fromaddr, email, text)
    server.quit()
    log.info('Email sent to '+str(email))


log.info('------------> Finish calculate grades and write xlsx report')


# exemple Koa-qualif
# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/bmd/lms/static/utils/completion_report.py

# exemple Koa-prod
# source /edx/app/edxapp/edxapp_env && /edx/app/edxapp/edx-platform/manage.py lms shell < /edx/app/edxapp/edx-themes/bmd/lms/static/utils/completion_report.py

