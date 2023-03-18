import logging
import os
from enum import Enum


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SHEET_URL = os.getenv('SHEET_URL')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

URL_SPREADSHEET_DOWNLOAD_CSV = 'https://docs.google.com/spreadsheets/d/{spreadsheetId}/export?format=csv'
URL_SPREADSHEET = 'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}?key={api_key}'
URL_AUTH_TOKEN = 'https://oauth2.googleapis.com/token'
URL_INSERT_EVENT = 'https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events'.format(calendarId='primary')

FIELDNAMES = ['Employee', 'Manager', 'Date', 'OneToOne', 'Review', 'Checkbox']


class GoogleServices(Enum):
    calendar = {'api_name': 'calendar',
                'api_version': 'v3',
                'scopes': ['https://www.googleapis.com/auth/calendar']}


CONFIG_EVENT = {
    'OneToOne': {'delta': 30,
                 'pre_summary': '1 to 1'},
    'Review': {'delta': 120,
               'pre_summary': 'Review'},
    'Description': 'YOUR DESCRIPTION'
}
