import pandas as pd

from config import FIELDNAMES, logger


def build_sheet_url_to_download_csv(raw_url: str) -> str:
    logger.info('Building url to download spreadsheet in csv format')
    doc_id = raw_url.split('/d/')[1].split('/')[0]
    return f'https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv'


def get_unchecked_list(raw_url):
    logger.info('Checking for unchecked...')
    url_to_download = build_sheet_url_to_download_csv(raw_url)
    df = pd.read_csv(url_to_download, names=FIELDNAMES)
    unchecked_list = df[df.Checkbox == 'FALSE'].to_dict('records')
    return unchecked_list
