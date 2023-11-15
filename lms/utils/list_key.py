# -*- coding: utf-8 -*-
#!/usr/bin/env python
import importlib
import zipfile

import sys
importlib.reload(sys)

import os
from io import BytesIO
from collections import OrderedDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.production")
os.environ.setdefault("LMS_CFG", "/edx/etc/lms.yml")
os.environ.setdefault("lms.envs.production,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
import string
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import BlockUsageLocator
from common.lib.xmodule.xmodule.modulestore.django import modulestore
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx import locator
from lms.djangoapps.wul_apps.models import WulCourseEnrollment
from common.djangoapps.student.models import User, UserProfile
from lms.djangoapps.courseware.models import StudentModule
from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_by_id


# entry point to the block_structure api.
from openedx.core.djangoapps.content.block_structure.api import get_course_in_cache

course_ids=["course-v1:hec-pole-emploi+IP+2023", "course-v1:hec-pole-emploi+IP_NEG+2023", "course-v1:hec-pole-emploi+NEG+2023", "course-v1:hec-pole-emploi+webinaire+2023"]

list_all_chapter_key = {}
list_scorms_names = dict()
for course_id in course_ids :
    # log.info(f"student module: {StudentModule.objects.filter(course_id__exact=course_id, module_type__exact='video')}")
    users = list()
    list_all_chapters = StudentModule.objects.filter(course_id__exact=course_id, module_type__exact="chapter").order_by("student_id")
    list_all_scorms = StudentModule.objects.filter(course_id__exact=course_id, module_type="scorm")
    list_chapter_keys = list()
    list_chapter_name = set()
    course_key = locator.CourseLocator.from_string(str(course_id))
    collected_block_structure = get_course_in_cache(course_key)
    print(course_id)
    for chapter in list_all_chapters:
        usage_key = UsageKey.from_string(str(chapter.module_state_key))
        #print(collected_block_structure)
        course_name = collected_block_structure.get_xblock_field(usage_key, "display_name")
        if course_name is None:
            continue
        #print(chapter)
        chapter_key = str(chapter.module_state_key)
        list_chapter_keys.append(chapter_key)
        list_chapter_name.add(course_name + " " + chapter_key)
    list_scorms_of_course = dict()
    for scorm in list_all_scorms:
        usage_key = UsageKey.from_string(str(scorm.module_state_key))
        scorm_name = collected_block_structure.get_xblock_field(usage_key, "display_name")
        #print(f"scorm_name: {scorm_name}")
        if str(scorm.module_state_key) in list_scorms_of_course.keys():
            continue
        usage_key = UsageKey.from_string(str(scorm.module_state_key))
        scorm_name = collected_block_structure.get_xblock_field(usage_key, "display_name")
        print(f"scorm_name: {scorm_name}")
        if scorm_name == None:
            continue
        list_scorms_of_course[str(scorm.module_state_key)] = scorm_name
    #print(list_chapter_name)
    list_scorms_names[course_id] = list_scorms_of_course
    list_chapter_keys = list(dict.fromkeys(list_chapter_keys))
    list_all_chapter_key[course_id] = list_chapter_keys
    #print(list_all_chapter_key)
print(list_scorms_names)
print(list_all_chapter_key)
