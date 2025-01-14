import boto3
import numpy as np

s3 = boto3.client(
    's3',
    aws_access_key_id='AKIATNVEVXUYCF3ZUQFB',
    aws_secret_access_key='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',
    region_name='eu-central-1'
)

file_content = s3.list_objects(Bucket='rag-chunks')

print(file_content)
