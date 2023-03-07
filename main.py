import json
import logging

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
        raw_content = requests.get(url).content
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
                start_date='07-03-2023 19:00',
                end_date='07-03-2023 19:10',
                email=email
            )
            event_service.create_event(body=body, send_notification=True)
            logging.info(f'  Event #{i} for {email} has been created.')
        logging.info(f'Created {len(self.unchecked_data)} event[s]')


if __name__ == '__main__':
    BaseEvent(SHEET_URL).main()
