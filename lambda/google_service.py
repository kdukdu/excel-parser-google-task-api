import json
from datetime import datetime, timedelta

import config
import requests


class GoogleEventAPI:
    def __init__(self):
        self.access_token = self.refresh_access_token()

    @staticmethod
    def refresh_access_token():
        response = requests.post(config.URL_AUTH_TOKEN,
                                 params={
                                     'client_id': config.CLIENT_ID,
                                     'client_secret': config.CLIENT_SECRET,
                                     'grant_type': 'refresh_token',
                                     'refresh_token': config.REFRESH_TOKEN},
                                 headers={
                                     'content-type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200:
            content = json.loads(response.content)
            access_token = content.get('access_token')
            return access_token

    @staticmethod
    def set_date_and_time(date: str, time: str, delta_days: int = 0):
        delta_days = timedelta(days=delta_days)
        date_time = datetime.strptime(
            f'{date} {time}', '%d-%m-%Y %H:%M'
        ) + delta_days
        return date_time.isoformat('T')

    def create_body(self,
                    summary: str,
                    description: str,
                    date: str,
                    delta: int,
                    email: str,
                    start_time: str = '19:00',
                    end_time: str = '19:30',
                    send_notification=True,
                    timezone: str = 'Europe/Minsk'):
        body = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': self.set_date_and_time(date, start_time, delta),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': self.set_date_and_time(date, end_time, delta),
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
            'sendNotifications': send_notification
        }
        return json.dumps(body)

    def create_event(self, body):
        response = requests.post(
            url=config.URL_INSERT_EVENT,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            data=body
        )
        return response.content
