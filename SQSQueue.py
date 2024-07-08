import os
import boto3
import json
import hashlib
import psycopg2
from botocore.config import Config
from datetime import datetime

# Set up environment variables for AWS
os.environ['AWS_ACCESS_KEY_ID'] = 'foobar'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'foobar'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Configure Boto3 to use Localstack
config = Config(
    region_name='us-east-1',
    retries={'max_attempts': 10, 'mode': 'standard'}
)

# Connect to Localstack SQS
sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', config=config)
queue_url = 'http://localhost:4566/000000000000/login-queue'

# Function to mask PII
def mask_pii(value):
    return hashlib.sha256(value.encode()).hexdigest()

# Receive messages from the queue
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=10
)

# Database connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS user_logins1 (
    user_id VARCHAR(128),
    device_type VARCHAR(32),
    masked_ip VARCHAR(256),
    masked_device_id VARCHAR(256),
    locale VARCHAR(32),
    app_version VARCHAR(32),  -- Change to VARCHAR
    create_date DATE
)
''')
conn.commit()

if 'Messages' in response:
    for message in response['Messages']:
        data = json.loads(message['Body'])

        # Mask PII
        data['device_id'] = mask_pii(data['device_id'])
        data['ip'] = mask_pii(data['ip'])

        # Provide default value if 'create_date' is missing
        create_date = data.get('create_date', datetime.now().date())

        # Ensure app_version is treated as VARCHAR
        app_version = data.get('app_version', '0.0.0')  # Default to '0.0.0' if missing

        # Insert data into Postgres
        cur.execute('''
        INSERT INTO user_logins1 (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (data['user_id'], data['device_type'], data['ip'], data['device_id'], data['locale'], app_version, create_date))
        conn.commit()

        # Delete message from the queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
else:
    print("No messages in queue.")

cur.close()
conn.close()
