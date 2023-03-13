import datetime
import logging
import os
from enum import Enum

from dotenv import load_dotenv

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SHEET_URL = os.getenv('SHEET_URL')
FIELDNAMES = ['Employee', 'Manager', 'Date', 'OneToOne', 'Review', 'Checkbox']


class GoogleServices(Enum):
    calendar = {'api_name': 'calendar',
                'api_version': 'v3',
                'scopes': ['https://www.googleapis.com/auth/calendar']}


CONFIG_EVENT = {
    'OneToOne': {'delta': datetime.timedelta(days=30),
                 'pre_summary': '1 to 1'},
    'Review': {'delta': datetime.timedelta(days=120),
               'pre_summary': 'Review'},
}
