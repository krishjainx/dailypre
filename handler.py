import os
import psycopg2
import json
import re
import uuid

def is_valid_mobile(mob_num):
    return bool(re.match(r'^\d{10}$', mob_num))

def is_valid_pan(pan_num):
    return bool(re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan_num))

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_PORT = os.environ['DB_PORT']
DB_HOST = os.environ['DB_HOST']


def get_users(event, context):
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
        # Query to fetch all users  so user_id, full_name, mob_num, pan_num
        fetch_query = "SELECT user_id, full_name, mob_num, pan_num FROM users;"
        cursor.execute(fetch_query)

        # Fetch all records
        records = cursor.fetchall()

        # Format records into JSON
        users = [
            {
                "user_id": user_id,
                "full_name": full_name,
                "mob_num": mob_num,
                "pan_num": pan_num
            }
            for user_id, full_name, mob_num, pan_num in records
        ]

        # Check if users list is empty
        if not users:
            return {'statusCode': 200, 'body': json.dumps({"users": []})}

        return {'statusCode': 200, 'body': json.dumps({"users": users})}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}

    finally:
        cursor.close()
        conn.close()


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

        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='users');")
        if not cursor.fetchone()[0]:
            # Create table if not exists (optional, based on your use case)
            cursor.execute("""
                CREATE TABLE users (
                    user_id UUID PRIMARY KEY,
                    full_name VARCHAR(255),
                    mob_num VARCHAR(20),
                    pan_num VARCHAR(20)
                );
            """)
            conn.commit()

        # Parse input
        data = json.loads(event['body'])
    

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


def delete_user(event, context):
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
        user_id = data.get('user_id', '')

        if not user_id:
            return {'statusCode': 400, 'body': json.dumps('User ID is required.')}

        # Check if user exists
        cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s);", (user_id,))
        if not cursor.fetchone()[0]:
            return {'statusCode': 404, 'body': json.dumps('User not found.')}

        # Delete user
        delete_query = "DELETE FROM users WHERE user_id = %s;"
        cursor.execute(delete_query, (user_id,))
        conn.commit()

        return {'statusCode': 200, 'body': json.dumps('User deleted successfully.')}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}

    finally:
        cursor.close()
        conn.close()