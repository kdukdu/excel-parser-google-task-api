from __future__ import print_function

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import logger, GoogleServices


class BaseGoogleApi:
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
            logger.error(err)
        else:
            return service

    @classmethod
    def get_service(cls, api_name):
        service = cls.create_service(**api_name)
        return service


class GoogleEventAPI(BaseGoogleApi):
    def __init__(self):
        self.service = self.get_service(GoogleServices.calendar.value)

    @staticmethod
    def create_body(summary, description, start_datetime,
                    end_datetime, email, timezone='Europe/Minsk'):
        body = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': timezone,
            },
            'attendees': [
                {'email': email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        return body

    def create_event(self, body, send_notification=False):
        self.service.events().insert(
            sendNotifications=send_notification,
            calendarId='primary',
            body=body
        ).execute()
