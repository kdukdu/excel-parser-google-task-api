from __future__ import print_function

import os
import os.path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


class BaseGoogleApi:
    TOKEN_FILE_NAME = os.getenv('TOKEN_FILE_NAME')
    API_NAME = os.getenv('API_NAME')
    API_VERSION = os.getenv('API_VERSION')
    SCOPES = ['https://www.googleapis.com/auth/tasks']

    @staticmethod
    def create_service(api_name, api_version, scopes):
        """Shows basic usage of the Tasks API.
        Prints the title and ID of the first 10 task lists.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        try:
            service = build(api_name, api_version, credentials=creds)
        except HttpError as err:
            print(err)
        else:
            return service

    @classmethod
    def get_service(cls):
        service = cls.create_service(api_name=cls.API_NAME,
                                     api_version=cls.API_VERSION,
                                     scopes=cls.SCOPES)
        return service


class GoogleTask(BaseGoogleApi):
    status = 'needsAction'

    def __init__(self):
        self.service = self.get_service()

    def create_tasklist(self, tasklist_name):
        response = self.service.tasklists().insert(
            body={'title': tasklist_name}
        ).execute()
        return response

    def get_list_tasklists(self):
        response = self.service.tasklists().list().execute()
        lst_items = response.get('items')
        return lst_items

    def delete_tasklist_by_name(self, tasklist_id):
        response = self.service.tasklists().delete(
            tasklist=tasklist_id
        ).execute()
        return response

    @classmethod
    def create_request_body(cls, title, notes=None, status=status, due=''):
        body = {
            "title": title,
            "notes": notes,
            "status": status,
            "due": due if not due else cls.get_timestamp(due)
        }
        return body

    def set_task(self, tasklist_id, body):
        response = self.service.tasks().insert(
            tasklist=tasklist_id,
            body=body
        ).execute()
        return response

    def get_tasks(self, tasklist_id):
        response = self.service.tasks().get(tasklist=tasklist_id)
        return response

    @staticmethod
    def get_timestamp(date: str) -> str:
        """
        Get string date formatted DD-MM-YYYY and return RFC 3339 timestamp
        """
        _format = '%d-%m-%Y'
        date = datetime.strptime(date, _format).astimezone().isoformat()
        return str(date)


my_tasklist_id = 'MDQ2ODI0ODU0Mjg2NjQ3MTQwMDA6MDow'
task_service = GoogleTask()
pd.set_option('display.max_columns', 10)
print(pd.DataFrame(task_service.get_list_tasklists()).head())
