from __future__ import print_function

import os
import os.path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class BaseGoogleAPI:
    GOOGLE_SERVICES = {
        'calendar': {'api_name': 'calendar',
                     'api_version': 'v3',
                     'scopes': ['https://www.googleapis.com/auth/calendar']}
    }

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
    def get_service(cls, api_name):
        data = cls.GOOGLE_SERVICES.get(api_name)
        if not data:
            raise ValueError('Error while creating google service')
        service = cls.create_service(**data)
        return service

    @staticmethod
    def get_timestamp(date: str) -> str:
        """
        Get string date formatted DD-MM-YYYY and return RFC 3339 timestamp
        """
        _format = '%d-%m-%Y %H:%M'
        date = datetime.strptime(date, _format).isoformat('T')
        return str(date)


class GoogleCalendarAPI(BaseGoogleAPI):
    def __init__(self):
        self.service = self.get_service('calendar')

    def get_calendarlist(self):
        response = self.service.calendarList().list().execute()
        return response

    def create_event_body(self, summary, description, email, start_time,
                          end_time, timezone='Europe/Minsk'):
        start = self.get_timestamp(start_time)
        end = self.get_timestamp(end_time)
        event_body = {
            'summary': summary,
            'description': description,
            'eventType': 'default',
            'start': {
                'dateTime': start,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end,
                'timeZone': timezone,
            },
            'attendees': [
                {'email': email}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        return event_body

    def create_event(self, body, send_notification=False):
        response = self.service.events().insert(
            sendNotifications=send_notification,
            calendarId='primary',
            body=body
        ).execute()
        return response
