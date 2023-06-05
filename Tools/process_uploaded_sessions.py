#!/usr/bin/env python

from clickerai_dataset_tools.google_storage import process_files

if __name__ == '__main__':
    # Set the paths to the source and destination buckets
    source_bucket_name = 'sessions-upload-v1'
    destination_bucket_screenshots_name = 'screenshots-v1'
    destination_bucket_events_logs_name = 'event-logs-v1'

    # Set the path to the credentials file
    credentials_path = '.secret.google-storage.json'

    process_files(source_bucket_name, destination_bucket_screenshots_name, destination_bucket_events_logs_name, credentials_path)



