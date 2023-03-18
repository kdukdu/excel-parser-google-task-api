import json
import logging

import pandas as pd
import requests
from config import (FIELDNAMES, GOOGLE_API_KEY, SHEET_URL, CONFIG_EVENT,
                    URL_SPREADSHEET, URL_SPREADSHEET_DOWNLOAD_CSV)
from google_service import GoogleEventAPI


class BaseEvent:
    def __init__(self, raw_url):
        self.raw_url = raw_url
        self.spreadsheet_id = self.get_spreadsheet_id_from_raw_url()
        self.rows_to_process = self.get_rows_to_process()

    def get_spreadsheet_id_from_raw_url(self):
        return self.raw_url.split('/d/')[-1].split('/')[0]

    def get_spreadsheet_title(self):
        url = URL_SPREADSHEET.format(spreadsheetId=self.spreadsheet_id,
                                     api_key=GOOGLE_API_KEY)
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(
                f'Cannot get title from a spreadsheet by your url: {self.raw_url}')
            raise requests.exceptions.InvalidURL
        raw_content = response.content
        content = json.loads(raw_content.decode('utf-8'))
        return content['properties']['title']

    def build_url_to_csv_download(self):
        url = URL_SPREADSHEET_DOWNLOAD_CSV.format(
            spreadsheetId=self.spreadsheet_id)
        return url

    def get_rows_to_process(self):
        logging.info('Getting rows to process...')
        url = self.build_url_to_csv_download()
        data = pd.read_csv(url, names=FIELDNAMES)
        unchecked_data = data[data['Checkbox'] == 'TRUE'].to_dict('records')
        return unchecked_data

    def main(self):
        if not self.rows_to_process:
            logging.info('There is no rows to process.')
            return None
        logging.info(f'There is[are] {len(self.rows_to_process)} value[s]')
        spreadsheet_title = self.get_spreadsheet_title()

        event_service = GoogleEventAPI()
        description = CONFIG_EVENT['Description']

        logging.info('Starting process of creating events...')
        for item in self.rows_to_process:
            summary = f'{item["Employee"]} - {spreadsheet_title}'
            email = item['Manager']
            date = item['Date']

            if item.get('OneToOne') == 'TRUE':
                pre_summary = CONFIG_EVENT['OneToOne']['pre_summary']
                delta = CONFIG_EVENT['OneToOne']['delta']
                summary_o2o = f'{pre_summary} - {summary}'
                body = event_service.create_body(summary_o2o, description,
                                                 date, delta, email)
                event_service.create_event(body)

            if item.get('Review') == 'TRUE':
                pre_summary = CONFIG_EVENT['Review']['pre_summary']
                delta = CONFIG_EVENT['Review']['delta']
                summary_review = f'{pre_summary} - {summary}'
                body = event_service.create_body(summary_review, description,
                                                 date, delta, email)
                event_service.create_event(body)


def handler(event, context):
    BaseEvent(SHEET_URL).main()
