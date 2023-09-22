import psycopg2
import bcrypt
from flask import Flask,request, jsonify    
from psycopg2 import sql

app = Flask(__name__)

db_config= {
    'database' : 'clein',
    'user'     : 'ganesa',
    'password' : 'ganesaganteng123.',
    'host'     : 'localhost',
    'port'     : 5432
}

def get_db_connection():
    connection = psycopg2.connect(**db_config)
    return connection

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    stored_password = hashed_password.decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try: 
        cursor.execute(
            """
            INSERT INTO users (full_name, username, password)
            VALUES (%s, %s, %s)
            """,
            (full_name, username, stored_password)
        )
        conn.commit()

        response = {'message': 'Signup successful'}
        return jsonify(response), 201
    
    except:
        conn.rollback()
        response = {'message': 'Signup failed'}
        return jsonify(response), 500
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_id, full_name, points, password
        FROM users
        WHERE username = %s OR email = %s
        """,
        (username_or_email, username_or_email)
    )
    user = cursor.fetchone()
    print(user)
    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        user_id, full_name, points = user[0], user[1], user[2]
        response = {
            'message': 'Login successful',
            'user_id': user_id,
            'full_name': full_name,
            'points': points
        }
        return jsonify(response), 200
    else:
        print(user)
        response = {'message': 'Invalid username or password'}
        return jsonify(response), 401

@app.route('/update-profile',methods = ['POST'])
def edit_profile():
    data = request.json
    user_id = data.get('id')
    new_full_name = data.get('full_name')
    new_username = data.get('username')
    new_email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try : 
        cursor.execute(
            """
            UPDATE users
            SET full_name = %s, username = %s, email = %s
            WHERE user_id = %s
            """,
            (new_full_name, new_username, new_email, user_id)
        )
        conn.commit()
        response = {'message': 'Profile update succesfully'}
        return jsonify(response), 201
    except:
        conn.rollback()
        response = {'message': 'Profile update failed'}
        return jsonify(response), 500
    finally:
        conn.close()

if __name__ ==  '__main__':
    app.run(debug=True, host='0.0.0.0')
