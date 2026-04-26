import boto3
from dotenv import load_dotenv
import os
import time
from supabase import create_client, Client

# FR-9: Backend Performance Testing
# Test with 50 retrieval and write each respectively to the
# backend looking for all different types of data in the relational databases.
# Ensure that 95% of the retrievals return within 2 seconds and every single
# write successfully is reflected in the database.

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


def test_write():

    for i in range(50):

        # to health_data
        table_health.put_item(Item={
            'user_id': str(i),
            'timestamp': str(i),
            'age': 30 + i,
            'context': 'test context',
            'fitness_goals': 'test goals',
            'gender': 'other',
            'height': 170 + i,
            'weight': 70 + i
            }
        )

        # to fitness_plan
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

        # to user_profiles
        table_user_prof.put_item(Item={
            'user_id': str(i)
        })

        # Write to S3 tables
        s3.upload_file('test.txt', bucket_name, f'test_user_{i}/test.txt')

        # Write to Supabase
        


    

def test_retrieval():

    num_in_time_dynamo = 0
    num_in_time_s3 = 0

    # Read from DynamoDB tables and measure time taken
    for i in range(50):

        start_time = time.time()
        response_health = table_health.get_item(Key={'user_id': str(i), 'timestamp': str(i)})
        end_time = time.time()
        print(f"Health data retrieval for user_id {i} took {end_time - start_time} seconds")
        if end_time - start_time <= 2:
            num_in_time_dynamo += 1


        start_time = time.time()
        response_fitness_plan = table_fitness_plan.get_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})
        end_time = time.time()
        print(f"Fitness plan retrieval for user_id {i} took {end_time - start_time} seconds")
        if end_time - start_time <= 2:
            num_in_time_dynamo += 1

        start_time = time.time()
        response_user_prof = table_user_prof.get_item(Key={'user_id': str(i)})
        end_time = time.time()
        print(f"User profile retrieval for user_id {i} took {end_time - start_time} seconds")
        if end_time - start_time <= 2:
            num_in_time_dynamo += 1

        # Read from S3 and measure time taken
        start_time = time.time()
        s3.download_file(bucket_name, f'test_user_{i}/test.txt', f'downloaded_test_{i}.txt')
        end_time = time.time()
        print(f"S3 file download for user_id {i} took {end_time - start_time} seconds")
        if end_time - start_time <= 2:
            num_in_time_s3 += 1

    return num_in_time_dynamo, num_in_time_s3

def delete_test_data():

    for i in range(50):
        # from health_data
        table_health.delete_item(Key={'user_id': str(i), 'timestamp': str(i)})

        # from fitness_plan
        table_fitness_plan.delete_item(Key={'user_id': str(i), 'workout_id': f'workout_{i}'})

        # from user_profiles
        table_user_prof.delete_item(Key={'user_id': str(i)})

        # from S3
        s3.delete_object(Bucket=bucket_name, Key=f'test_user_{i}/test.txt')
        os.remove(f'downloaded_test_{i}.txt')

def run_test():

    print("Starting backend performance test...")
    print("Beginning writes...")
    test_write()

    print("\n\n")
    print("Writes completed. Beginning retrievals...")
    num_in_time_dynamo, num_in_time_s3 = test_retrieval()

    print("\n\n")
    print("Retrievals completed. Deleting test data...")
    delete_test_data()

    print("\n\n")
    print("Test completed. All test data deleted.")


    print("\n\n")
    print("################################################################################################################################")
    print(f"DynamoDB retrievals completed within 2 seconds: {num_in_time_dynamo}, {num_in_time_dynamo/150*100}% Success Rate")
    print(f"S3 retrievals completed within 2 seconds: {num_in_time_s3}, {num_in_time_s3/50*100}% Success Rate")
    print("################################################################################################################################")



if __name__ == "__main__":
    run_test()