import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SHEET_URL = os.getenv('SHEET_URL')
FIELDNAMES = os.getenv('SHEET_FIELDNAMES').split()
