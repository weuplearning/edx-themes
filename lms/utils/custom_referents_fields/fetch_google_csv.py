# -*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import json
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import config

import logging
log = logging.getLogger()

def fetch_google_drive_file():

    
    credentials_path = config.credentials_path
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)
    export_mime_type = 'text/csv'  # Excel

    file_id = config.google_sheets_file_id
    request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
    
    file_stream = io.BytesIO()
    
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Téléchargement: {int(status.progress() * 100)}%")

    file_path = config.csv_path # Change extension based on export_mime_type
    with open(file_path, "wb") as f:
        f.write(file_stream.getvalue())

    print(f"Fichier téléchargé sous : {file_path}")

fetch_google_drive_file()

# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/fetch_google_csv.py 