import json

import pandas as pd
import requests

from config import logger, SHEET_URL, FIELDNAMES, GOOGLE_API_KEY
from google_service import GoogleCalendarAPI


class Base:
    def __init__(self, raw_url):
        self.raw_url = raw_url
        self.unchecked_list = self.get_unchecked_list()

    def build_sheet_url_to_download_csv(self) -> str:
        logger.info('Building url to download spreadsheet in csv format.')
        doc_id = self.raw_url.split('/d/')[1].split('/')[0]
        return f'https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv'

    def get_unchecked_list(self):
        logger.info('Checking for unchecked...')
        url_to_download = self.build_sheet_url_to_download_csv()
        df = pd.read_csv(url_to_download, names=FIELDNAMES)
        unchecked_list = df[df.Checkbox == 'FALSE'].to_dict('records')
        return unchecked_list

    def get_spreadsheet_title(self) -> dict:
        """
        Get raw url of your google sheet and return description info about your spreadsheet.
        :return: Content: {'spreadsheetId': 'spreadsheet_id', 'properties': {'title': 'spreadsheet_title', 'locale': 'en_US', 'autoRecalc': 'ON_CHANGE', 'timeZone': 'Europe/Moscow', 'defaultFormat': {'backgroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'padding': {'top': 2, 'right': 3, 'bottom': 2, 'left': 3}, 'verticalAlignment': 'BOTTOM', 'wrapStrategy': 'OVERFLOW_CELL', 'textFormat': {'foregroundColor': {}, 'fontFamily': 'arial,sans,sans-serif', 'fontSize': 10, 'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'foregroundColorStyle': {'rgbColor': {}}}, 'backgroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}}, 'spreadsheetTheme': {'primaryFontFamily': 'Arial', 'themeColors': [{'colorType': 'TEXT', 'color': {'rgbColor': {}}}, {'colorType': 'BACKGROUND', 'color': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}}, {'colorType': 'ACCENT1', 'color': {'rgbColor': {'red': 0.25882354, 'green': 0.52156866, 'blue': 0.95686275}}}, {'colorType': 'ACCENT2', 'color': {'rgbColor': {'red': 0.91764706, 'green': 0.2627451, 'blue': 0.20784314}}}, {'colorType': 'ACCENT3', 'color': {'rgbColor': {'red': 0.9843137, 'green': 0.7372549, 'blue': 0.015686275}}}, {'colorType': 'ACCENT4', 'color': {'rgbColor': {'red': 0.20392157, 'green': 0.65882355, 'blue': 0.3254902}}}, {'colorType': 'ACCENT5', 'color': {'rgbColor': {'red': 1, 'green': 0.42745098, 'blue': 0.003921569}}}, {'colorType': 'ACCENT6', 'color': {'rgbColor': {'red': 0.27450982, 'green': 0.7411765, 'blue': 0.7764706}}}, {'colorType': 'LINK', 'color': {'rgbColor': {'red': 0.06666667, 'green': 0.33333334, 'blue': 0.8}}}]}}, 'sheets': [{'properties': {'sheetId': 0, 'title': 'Sheet1', 'index': 0, 'sheetType': 'GRID', 'gridProperties': {'rowCount': 1000, 'columnCount': 26}}}], 'spreadsheetUrl': 'spreadsheet_url'}
        """
        logger.info('Getting the name of spreadsheet')
        spreadsheet_id = self.raw_url.split('/d/')[1].split('/')[0]
        url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?key={GOOGLE_API_KEY}&alt=json'
        bytes_data = requests.get(url).content
        content = json.loads(bytes_data.decode('utf-8'))
        return content.get('properties').get('title')

    def main(self):
        if not self.unchecked_list:
            logger.info('BREAK! There is no unchecked values.')
            return None

        logger.info(f'There are {len(self.unchecked_list)} unchecked event[s].')

        calendar_service = GoogleCalendarAPI()
        title = self.get_spreadsheet_title()

        logger.info('Creating events for unchecked:')
        for i, item in enumerate(self.unchecked_list, 1):
            summary = f'{title} - {item["Employee"]}'
            description = f'Link to the table {SHEET_URL}'
            email = item['Manager']
            body = calendar_service.create_event_body(
                summary=summary,
                description=description,
                email=email,
                start_time='07-03-2023 19:00',
                end_time='07-03-2023 19:30'
            )
            calendar_service.create_event(body=body, send_notification=True)
            logger.info(f'  Event #{i} created for {email}')
        logger.info('There is no more events to create.')
        logger.info('Process finished.')


if __name__ == '__main__':
    Base(SHEET_URL).main()
