import json
import logging
from datetime import date, time, datetime

import pandas as pd
import requests

from config import FIELDNAMES, GOOGLE_API_KEY, SHEET_URL
from google_service import GoogleEventAPI


class BaseEvent:
    def __init__(self, raw_url):
        self.raw_url = raw_url
        self.spreadsheet_id = self.get_spreadsheet_id_from_raw_url()
        self.unchecked_data = self.get_unchecked_data()

    def get_spreadsheet_id_from_raw_url(self):
        return self.raw_url.split('/d/')[-1].split('/')[0]

    def get_spreadsheet_title(self):
        url = f'https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}?key={GOOGLE_API_KEY}'
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(
                f'Cannot get title from a spreadsheet by your url: {self.raw_url}')
            raise requests.exceptions.InvalidURL
        raw_content = response.content
        content = json.loads(raw_content.decode('utf-8'))
        return content['properties']['title']

    def build_url_to_csv_download(self):
        url = f'https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv'
        return url

    def get_unchecked_data(self):
        logging.info('Getting unchecked data...')
        url = self.build_url_to_csv_download()
        data = pd.read_csv(url, names=FIELDNAMES)
        unchecked_data = data[data['Checkbox'] == 'FALSE'].to_dict('records')
        return unchecked_data

    @staticmethod
    def set_datetime(hour, minute):
        date_time = datetime.combine(
            date.today(),
            time(hour=hour, minute=minute)
        ).isoformat('T')
        return date_time

    def main(self):
        if not self.unchecked_data:
            logging.info('There is no unchecked data.')
            return None

        logging.info(f'There is[are] {len(self.unchecked_data)} value[s]')
        event_service = GoogleEventAPI()
        spreadsheet_title = self.get_spreadsheet_title()

        logging.info('Starting process of creating events...')
        for i, item in enumerate(self.unchecked_data, 1):
            summary = f'{item["Employee"]} - {spreadsheet_title}'
            description = f'Link to google sheets {self.raw_url}'
            email = item['Manager']
            body = event_service.create_body(
                summary=summary,
                description=description,
                start_datetime=self.set_datetime(hour=19, minute=0),
                end_datetime=self.set_datetime(hour=19, minute=30),
                email=email
            )
            event_service.create_event(body=body, send_notification=True)
            logging.info(f'  Event #{i} for {email} has been created.')
        logging.info(f'Created {len(self.unchecked_data)} event[s]')


if __name__ == '__main__':
    BaseEvent(SHEET_URL).main()
