import boto3
from dotenv import load_dotenv
import os
import time
import pytest

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')

bucket_name = 'fitness-form-videos'

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

dynamo = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)
table_health = dynamo.Table('health_data')
table_fitness_plan = dynamo.Table('fitness_plan')
table_user_prof = dynamo.Table('user_profiles')

THRESHOLD_SECONDS = 2.0
PASS_RATE = 0.90
NUM_SAMPLES = 50


def measure_retrieval_times():
    dynamo_times = []
    s3_times = []

    for i in range(NUM_SAMPLES):
        start = time.time()
        table_health.get_item(Key={'user_id': str(i), 'timestamp': str(i)})
        dynamo_times.append(time.time() - start)

        start = time.time()
        table_fitness_plan.get_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})
        dynamo_times.append(time.time() - start)

        start = time.time()
        table_user_prof.get_item(Key={'user_id': str(i)})
        dynamo_times.append(time.time() - start)

        start = time.time()
        s3.download_file(bucket_name, f'test_user_{i}/test.txt', f'/tmp/downloaded_test_{i}.txt')
        s3_times.append(time.time() - start)

    return dynamo_times, s3_times


def test_dynamo_retrieval_speed():
    dynamo_times, _ = measure_retrieval_times()

    within_threshold = sum(1 for t in dynamo_times if t <= THRESHOLD_SECONDS)
    pass_rate = within_threshold / len(dynamo_times)

    print(f"\nDynamoDB: {within_threshold}/{len(dynamo_times)} retrievals within {THRESHOLD_SECONDS}s ({pass_rate:.0%})")
    assert pass_rate >= PASS_RATE, (
        f"DynamoDB retrieval pass rate {pass_rate:.0%} is below the required {PASS_RATE:.0%}. "
        f"Slowest query: {max(dynamo_times):.3f}s"
    )


def test_s3_retrieval_speed():
    _, s3_times = measure_retrieval_times()

    within_threshold = sum(1 for t in s3_times if t <= THRESHOLD_SECONDS)
    pass_rate = within_threshold / len(s3_times)

    print(f"\nS3: {within_threshold}/{len(s3_times)} retrievals within {THRESHOLD_SECONDS}s ({pass_rate:.0%})")
    assert pass_rate >= PASS_RATE, (
        f"S3 retrieval pass rate {pass_rate:.0%} is below the required {PASS_RATE:.0%}. "
        f"Slowest download: {max(s3_times):.3f}s"
    )