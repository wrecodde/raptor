
import logging

from datetime import datetime
from typing import Callable

from environs import Env

from notion_client import Client
from notion_client.errors import APIResponseError

env = Env()
env.read_env()

notion = Client(
    auth=env.str('NOTION_TOKEN'),
    log_level = env.str('NOTION_LOG_LEVEL')
)

DEFAULT_DB = env.str('NOTION_DEFAULT_DATABASE', None)

def get_database(database_id: str = DEFAULT_DB) -> list:
    """Retrieve all rows from a Notion Database
    
    Returns an empty list if the request fails
    """

    query = {
        "database_id": database_id
    }

    accumulator = []
    
    try: 
        response = notion.databases.query(**query)
        if response['has_more']:
            logging.info('This database has more items, but they are not being fetched')
        
        accumulator.extend(response['results'])
        return accumulator

    except APIResponseError as error:
        logging.error(error.body['message'])
        return []

def parse_database(records: list):
    """Convert Notion Database Properties to Python Type"""
    parsed_db = []

    for raw in records:
        record = {}

        for prop_name, prop in raw['properties'].items():
            handler = property_handler(prop['type'])
            prop_value = handler(prop) if handler != None else None
            record[prop_name] = prop_value
        
        parsed_db.append(record)
    
    return parsed_db

def property_handler(property_type: str) -> Callable:
    handler = {
        "title": prop_title,
        "url": prop_url,
        "select": prop_select,
        "rich_text": prop_rich_text,
        "date": prop_date,
        "multi_select": prop_multi_select,
        "number": prop_number
    }

    return handler.get(property_type, None)

def prop_title(prop: dict) -> str:
    """Parse Title property"""

    title_field = prop.get('title', None)
    plain_text = ""
    if type(title_field) is not list:
        logging.debug("title field not found")
        return plain_text

    plain_text = title_field[0].get('plain_text', '')
    return plain_text

def prop_rich_text(prop: dict) -> str:
    """Parse Rich Text property"""

    # TODO: properly parse this field type
    rich_text = prop.get('rich_text', [])
    if rich_text is not []:
        rich_text = [block['plain_text'] for block in rich_text]

    return ''.join(rich_text)


def prop_number(prop: dict) -> int:
    """Parse Number property"""

    number_field = prop.get('number', None)
    return number_field

def prop_select(prop: dict) -> str:
    """Parse Select property"""

    select_field = prop.get('select', None)
    if select_field is not None:
        return select_field['name']
    
    else:
        return ''

def prop_multi_select(prop: dict) -> str:
    """Parse Multi-Select property"""

    multi_select_field = prop.get('multi_select', [])
    if multi_select_field is not []:
        multi_select_field = [block['name'] for block in multi_select_field]

    return ', '.join(multi_select_field)

def prop_date(prop: dict) -> str:
    """Parse Date property"""

    date_field = prop.get('date', None)
    if date_field is not None:
        start_date = date_field.get('start')
        
        # parsed = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f+%z')
        return start_date
    else:
        return ''

def prop_people(prop):
    pass

def prop_files(prop):
    pass

def prop_checkbox(prop):
    pass

def prop_url(prop: dict) -> str:
    """Parse URL property"""
    
    url = prop.get('url', '')
    return url

def prop_email(prop):
    pass

def prop_phone_number(prop):
    pass

def prop_formula(prop):
    pass

def prop_relation(prop):
    pass

def prop_rollup(prop):
    pass

def prop_created_time(prop):
    pass

def prop_created_by(prop):
    pass

def prop_last_edited_time(prop):
    pass

def prop_last_edited_by(prop):
    pass

def prop_status(prop):
    pass


