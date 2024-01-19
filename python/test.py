import boto3
import subprocess
import os
from datetime import datetime

# AWS Configuration
s3_bucket = "openhab-dusty"
aws_region = "us-east-1"
s3_client = boto3.client('s3', region_name=aws_region)
print(s3_client.list_objects_v2(Bucket=s3_bucket))
