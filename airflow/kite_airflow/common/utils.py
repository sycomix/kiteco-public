import ast
import datetime
import time
import uuid
import json

from airflow.models import Variable
import kite_metrics


kite_status_config = kite_metrics.load_context('kite_status')


def is_production():
    return Variable.get('env', 'dev') == 'production'


def get_supported_languages():
    return kite_status_config['languages']


def get_unique_suffix():
    return f'-{get_date_time_in_ISO()}-{uuid.uuid4().hex}.json'


def get_date_time_in_ISO():
    date_time = datetime.datetime.fromtimestamp(time.time())
    return f'{date_time.isoformat()}Z'


def string_to_dict(string):
    return ast.literal_eval(string.replace('=', ':'))
