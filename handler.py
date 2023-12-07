import json
import re
import uuid
import psycopg2
import os

# Database connection details
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']

def is_valid_mobile(mob_num):
    return bool(re.match(r'^\d{10}$', mob_num))

def is_valid_pan(pan_num):
    return bool(re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan_num))

def create_user(event, context):
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        host=DB_HOST, 
        port=DB_PORT
    )
    cursor = conn.cursor()

    try:
        # Parse input
        data = json.loads(event['body'])

        # Validation
        full_name = data.get('full_name', '').strip()
        mob_num = data.get('mob_num', '')
        pan_num = data.get('pan_num', '')

        if not full_name:
            return {'statusCode': 400, 'body': json.dumps('Full name is required.')}

        if not is_valid_mobile(mob_num):
            return {'statusCode': 400, 'body': json.dumps('Invalid mobile number. Must be a 10-digit number.')}

        if not is_valid_pan(pan_num):
            return {'statusCode': 400, 'body': json.dumps('Invalid PAN number.')}

        # Generate a UUID for the new user
        user_id = str(uuid.uuid4())

        # Insert data into database
        insert_query = """INSERT INTO users (user_id, full_name, mob_num, pan_num) VALUES (%s, %s, %s, %s);"""
        cursor.execute(insert_query, (user_id, full_name, mob_num, pan_num))
        conn.commit()

        return {'statusCode': 200, 'body': json.dumps('User created successfully.')}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}

    finally:
        cursor.close()
        conn.close()
