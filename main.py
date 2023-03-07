from config import logger, SHEET_URL
from google_service import GoogleCalendarAPI, get_spreadsheet_info
from parser import get_unchecked_list


def create_event_for_unchecked(raw_url):
    unchecked_list = get_unchecked_list(raw_url)
    if not unchecked_list:
        logger.info('BREAK! There is no unchecked values')
        return None

    logger.info(f'There are {len(unchecked_list)} unchecked events')
    calendar_service = GoogleCalendarAPI()
    content = get_spreadsheet_info(raw_url)
    title = content['properties']['title']

    logger.info('Creating events for unchecked')
    for i, item in enumerate(unchecked_list, 1):
        summary = f'{title} - {item["Employee"]}'
        description = f'Link to the table {SHEET_URL}'
        email = item['Manager']
        body = calendar_service.create_event_body(
            summary=summary,
            description=description,
            email='kocherizhkin@gmail.com',
            start_time='07-03-2023 19:00',
            end_time='07-03-2023 19:30'
        )
        calendar_service.create_event(body=body, send_notification=True)
        logger.info(f'Event #{i} created for {email}')
    logger.info('Process finished')


create_event_for_unchecked(SHEET_URL)
