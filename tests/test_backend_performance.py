import boto3
import os
import time
import pytest

BUCKET_NAME = 'fitness-form-videos'
NUM_SAMPLES = 50
THRESHOLD = 2.0
PASS_RATE = 0.90

s3 = None
table_health = None
table_fitness_plan = None
table_user_prof = None

def setup_module():
    global s3, table_health, table_fitness_plan, table_user_prof

    s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'])
    dynamo = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table_health = dynamo.Table('health_data')
    table_fitness_plan = dynamo.Table('fitness_plan')
    table_user_prof = dynamo.Table('user_profiles')

    # Write test data
    for i in range(NUM_SAMPLES):
        table_health.put_item(Item={'user_id': str(i), 'timestamp': str(i), 'age': 30 + i})
        table_fitness_plan.put_item(Item={'user_id': str(i), 'workout_id': f'workout_{i}'})
        table_user_prof.put_item(Item={'user_id': str(i)})
        s3.upload_file('tests/test.txt', BUCKET_NAME, f'test_user_{i}/test.txt')


def teardown_module():
    for i in range(NUM_SAMPLES):
        table_health.delete_item(Key={'user_id': str(i), 'timestamp': str(i)})
        table_fitness_plan.delete_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})
        table_user_prof.delete_item(Key={'user_id': str(i)})
        s3.delete_object(Bucket=BUCKET_NAME, Key=f'test_user_{i}/test.txt')


def test_dynamo_retrieval_speed():
    times = []
    for i in range(NUM_SAMPLES):
        for fn in [
            lambda: table_health.get_item(Key={'user_id': str(i), 'timestamp': str(i)}),
            lambda: table_fitness_plan.get_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'}),
            lambda: table_user_prof.get_item(Key={'user_id': str(i)}),
        ]:
            start = time.time()
            fn()
            times.append(time.time() - start)

    pass_rate = sum(1 for t in times if t <= THRESHOLD) / len(times)
    assert pass_rate >= PASS_RATE, f"DynamoDB pass rate {pass_rate:.0%} < {PASS_RATE:.0%}. Slowest: {max(times):.3f}s"


def test_s3_retrieval_speed():
    times = []
    for i in range(NUM_SAMPLES):
        start = time.time()
        s3.download_file(BUCKET_NAME, f'test_user_{i}/test.txt', f'/tmp/dl_{i}.txt')
        times.append(time.time() - start)

    pass_rate = sum(1 for t in times if t <= THRESHOLD) / len(times)
    assert pass_rate >= PASS_RATE, f"S3 pass rate {pass_rate:.0%} < {PASS_RATE:.0%}. Slowest: {max(times):.3f}s"