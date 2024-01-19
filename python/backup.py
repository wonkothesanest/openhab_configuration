import boto3
import subprocess
import os
import configparser
import shutil
from datetime import datetime


config = configparser.ConfigParser()
config.read('/etc/secrets.ini')
access_key = config['aws'].get('access_key')
secret_key = config['aws'].get('secret_key')
# AWS Configuration
s3_bucket = "openhab-dusty"
aws_region = "us-east-1"

# OpenHAB and InfluxDB Backup Configuration
backup_dir = "/home/dusty/oh_backup"
openhab_backup_filename = f"openhab-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
influxdb_backup_filename = f"influxdb-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
gpt_responses_filename = f"chat-responses-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
openhab_backup_path = os.path.join(backup_dir, openhab_backup_filename)
influxdb_backup_path = os.path.join(backup_dir, influxdb_backup_filename)
influxdb_backup_path_tar = influxdb_backup_path + ".tar.gz"
influxdb_backup_filename_tar = influxdb_backup_filename + ".tar.gz"
gpt_responses_path = os.path.join(backup_dir, "chat_responses.json")

# Create an OpenHAB backup
print("Creating OpenHAB backup...")
subprocess.run(["openhab-cli", "backup", openhab_backup_path], check=True)

# Backup InfluxDB
print("Backing up InfluxDB...")
subprocess.run(["influxd", "backup", "-portable", influxdb_backup_path], check=True)

# Initialize S3 client
s3_client = boto3.client('s3', region_name=aws_region)

# Function to upload file to S3
def upload_to_s3(file_path, filename):
    print(f"Uploading {filename} to S3...")
    with open(file_path, "rb") as f:
        s3_client.upload_fileobj(f, s3_bucket, filename)

# Zip the influxdb directory
shutil.make_archive(influxdb_backup_path, 'gztar', influxdb_backup_path)

# Upload OpenHAB and InfluxDB backups to S3
upload_to_s3(openhab_backup_path, openhab_backup_filename)
upload_to_s3(influxdb_backup_path_tar, influxdb_backup_filename_tar)
dt = datetime.now()
upload_to_s3(gpt_responses_path, f"gpt-responses/{dt.strftime('%Y')}/{dt.strftime('%m')}/{gpt_responses_filename}")

# Clean up local files
os.remove(openhab_backup_path)
shutil.rmtree(influxdb_backup_path)
os.remove(influxdb_backup_path_tar)
os.remove(gpt_responses_path)

# Rotate backups: keep only latest 4
def rotate_backups(bucket, prefix):
    backups = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)['Contents']
    sorted_backups = sorted(backups, key=lambda k: k['LastModified'])

    while len(sorted_backups) > 4:
        old_backup = sorted_backups.pop(0)
        print(f"Deleting old backup: {old_backup['Key']}")
        s3_client.delete_object(Bucket=bucket, Key=old_backup['Key'])

rotate_backups(s3_bucket, 'openhab-backup-')
rotate_backups(s3_bucket, 'influxdb-backup-')

print("Backup process completed.")

