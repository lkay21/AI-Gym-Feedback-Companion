import os
import time
import boto3
import pytest
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

bucket_name = 'fitness-form-videos'
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION)

dynamo = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION)
table_health = dynamo.Table('health_data')
table_fitness_plan = dynamo.Table('fitness_plan')
table_user_prof = dynamo.Table('user_profiles')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@pytest.fixture(scope="module")
def setup_test_files():
    # Create a dummy file for S3 upload
    with open('test.txt', 'w') as f:
        f.write('test content')
    yield
    os.remove('test.txt')
    for i in range(50):
        try:
            os.remove(f'downloaded_test_{i}.txt')
        except FileNotFoundError:
            pass

def test_backend_performance(setup_test_files):
    # Write phase
    for i in range(50):
        table_health.put_item(Item={
            'user_id': str(i),
            'timestamp': str(i),
            'age': 30 + i,
            'context': 'test context',
            'fitness_goals': 'test goals',
            'gender': 'other',
            'height': 170 + i,
            'weight': 70 + i
        })
        table_fitness_plan.put_item(Item={
            'user_id': str(i),
            'workout_id': f'workout_{i}',
            'date_of_workout': '2024-01-01',
            'exercise_description': 'test exercises',
            'exercise_name': 'test exercise',
            'expected_cals_burned': 500 + i,
            'muscle_group': 'test muscle group',
            'rep_count': 10 + i,
            'weight_to_lift_suggestion': 20 + i
        })
        table_user_prof.put_item(Item={
            'user_id': str(i)
        })
        s3.upload_file('test.txt', bucket_name, f'test_user_{i}/test.txt')

    # Retrieval phase
    num_in_time_dynamo = 0
    num_in_time_s3 = 0
    for i in range(50):
        start = time.time()
        resp = table_health.get_item(Key={'user_id': str(i), 'timestamp': str(i)})
        assert 'Item' in resp
        if time.time() - start <= 2:
            num_in_time_dynamo += 1
        start = time.time()
        resp = table_fitness_plan.get_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})
        assert 'Item' in resp
        if time.time() - start <= 2:
            num_in_time_dynamo += 1
        start = time.time()
        resp = table_user_prof.get_item(Key={'user_id': str(i)})
        assert 'Item' in resp
        if time.time() - start <= 2:
            num_in_time_dynamo += 1
        start = time.time()
        s3.download_file(bucket_name, f'test_user_{i}/test.txt', f'downloaded_test_{i}.txt')
        assert os.path.exists(f'downloaded_test_{i}.txt')
        if time.time() - start <= 2:
            num_in_time_s3 += 1
    assert num_in_time_dynamo >= 0.95 * 150
    assert num_in_time_s3 >= 0.95 * 50

    # Delete phase
    for i in range(50):
        table_health.delete_item(Key={'user_id': str(i), 'timestamp': str(i)})
        table_fitness_plan.delete_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})
        table_user_prof.delete_item(Key={'user_id': str(i)})
        s3.delete_object(Bucket=bucket_name, Key=f'test_user_{i}/test.txt')
        try:
            os.remove(f'downloaded_test_{i}.txt')
        except FileNotFoundError:
            pass
