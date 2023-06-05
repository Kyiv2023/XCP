
import os
import shutil
from google.cloud import storage
from tqdm import tqdm
from zipfile import ZipFile
from .clicker_zip import unpack_clicker_zip


import os
import shutil
import concurrent.futures
from tqdm import tqdm
from google.cloud import storage

import multiprocessing

# get the number of CPU cores
num_cores = multiprocessing.cpu_count()


data_dir = ".data"


def upload_files(bucket, directory_path, file_extensions, description):
    """
    Uploads files with specified extensions from a directory to a given bucket.
    """
    # Get all the files with specified extensions in the directory
    files = [f for f in os.listdir(directory_path) if f.lower().endswith(file_extensions)]

    # Upload each file to the bucket
    for filename in files:
        blob = bucket.blob(filename)
        blob.upload_from_filename(os.path.join(directory_path, filename))


def process_zip_file(blob, destination_bucket_screenshots, destination_bucket_events_logs):
    """
    Processes a zip file, extracting its contents and uploading files to the given buckets.
    """
    # Get the zip file name
    zip_file_name = os.path.basename(blob.name)



    # Download the file to local disk
    blob.download_to_filename(f'{data_dir}/{zip_file_name}')

    session_id = os.path.splitext(zip_file_name)[0]
    # Extract the contents of the zip file
    unpack_clicker_zip(f'{data_dir}/{zip_file_name}', f'{data_dir}/{session_id}')

    # Create a list of tasks to upload files to the screenshots and events logs buckets
    tasks = []

    # Upload all image files to the screenshots bucket
    tasks.append((destination_bucket_screenshots, f'{data_dir}/{session_id}', ('.tiff', '.png', '.jpg', '.jpeg', '.gif'), f"UP screenshots <{session_id[:7]}>"))

    # Upload all data files to the events logs bucket
    tasks.append((destination_bucket_events_logs, f'{data_dir}/{session_id}', ('.csv', '.json', '.yaml'), f"UP events <{session_id[:7]}>"))

    # Execute the tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_task, tasks), total=len(tasks)))

    # Delete the temporary zip file
    os.remove(f'{data_dir}/{zip_file_name}')

    # Delete the contents of the extracted directory
    for filename in os.listdir(f'{data_dir}/{os.path.splitext(zip_file_name)[0]}'):
        os.remove(os.path.join(f'{data_dir}/{os.path.splitext(zip_file_name)[0]}', filename))


def process_task(args):
    """
    Processes a single task of uploading files to a bucket.
    """
    bucket, directory_path, file_extensions, description = args
    upload_files(bucket, directory_path, file_extensions, description)

def process_files(source_bucket_name, destination_bucket_screenshots_name, destination_bucket_events_logs_name, credentials_path):
    """
    Processes all files in a source bucket, extracts any zip files to a local directory,
    uploads image files to a screenshots bucket and data files to an events logs bucket.
    """


    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    else:
        shutil.rmtree(data_dir)
        os.makedirs(data_dir)

    # Authenticate with Google Cloud Storage using the credentials file
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    storage_client = storage.Client()

    # Get the source bucket
    source_bucket = storage_client.bucket(source_bucket_name)

    # Get the destination buckets
    destination_bucket_screenshots = storage_client.bucket(destination_bucket_screenshots_name)
    destination_bucket_events_logs = storage_client.bucket(destination_bucket_events_logs_name)

    # Loop over all the files in the source bucket
    blobs = source_bucket.list_blobs()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for blob in tqdm(blobs, desc="DOWN"):
            # Get the file extension
            file_extension = os.path.splitext(blob.name)[1].lower()

            # Only process zip files
            if file_extension != '.zip':
                continue

            future = executor.submit(process_zip_file, blob, destination_bucket_screenshots, destination_bucket_events_logs)
            futures.append(future)

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="UP"):
            future.result()
