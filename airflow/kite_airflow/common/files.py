import csv
import codecs

from airflow.hooks.S3_hook import S3Hook

from kite_airflow.common import utils
from kite_airflow.common import configs


def get_scratch_csv_dict_reader(ti, task_id, sub_directory):
    s3 = S3Hook(configs.AWS_CONN_ID)
    filename = ti.xcom_pull(task_ids=task_id)
    s3key = s3.get_key(
        f'{configs.DIR_SCRATCH_SPACE}/{sub_directory}/{filename}.csv',
        configs.BUCKET,
    )

    return csv.DictReader(
        codecs.getreader("utf-8")(s3key.get()['Body'])
    )


def get_full_scratch_space_csv(ti, task_id, sub_directory):
    reader = get_scratch_csv_dict_reader(ti, task_id, sub_directory)
    return list(reader)


def get_line_of_scratch_space_csv(ti, task_id, sub_directory):
    reader = get_scratch_csv_dict_reader(ti, task_id, sub_directory)
    yield from enumerate(reader, start=1)


def get_csv_file_as_dict(bucket, file_path):
    s3 = S3Hook(configs.AWS_CONN_ID)
    s3key = s3.get_key(file_path, bucket)
    reader = csv.DictReader(codecs.getreader("utf-8")(s3key.get()['Body']))
    return list(reader)


def write_dict_on_csv_file(bucket, file_path, data_list):
    if(len(data_list) == 0):
        return

    s3_hook = S3Hook(configs.AWS_CONN_ID)
    keys = data_list[0].keys()
    upload_data_list = [','.join(keys)]
    for item in data_list:
       values = item.values()
       upload_data_list.append(','.join(values))

    s3_hook.load_bytes(
        '\n'.join(upload_data_list).encode('utf-8'),
        file_path,
        bucket,
        replace=True,
    )
