import traceback
import psycopg2
import bcrypt
import jwt
from flask import Flask,request, jsonify    
from psycopg2 import sql
from datetime import datetime, timedelta
import os

app = Flask(__name__)

secret_key = str(os.environ.get('CLEIN_SECRET_KEY'))

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

def get_exchangeable_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT barang_name, barang_points, barang_stok FROM barang_tukar")
    items = cursor.fetchall()
    conn.close()
    return items

@app.route('/')
def land():
    return "hello world!"

@app.route('/signup_admin', methods=['POST'])
def signup_admin():
    data = request.json
    username = data.get('admin_username')
    password = data.get('admin_pass')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    stored_password = hashed_password.decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try: 
        cursor.execute(
            """
            INSERT INTO admins (admin_username, admin_pass)
            VALUES (%s, %s)
            """,
            (username, stored_password)
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

@app.route('/login-admin', methods=['POST'])
def login_admin():
    data = request.json
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id_admin, admin_username, admin_pass
        FROM admins
        WHERE admin_username = %s OR admin_email = %s
        """,
        (username_or_email, username_or_email)
    )
    admin = cursor.fetchone()
    print(admin)
    if admin and bcrypt.checkpw(password.encode('utf-8'), admin[2].encode('utf-8')):
        id_admin, admin_username = admin[0], admin[1]
        response = {
            'message': 'Login successful',
            'id_admin': id_admin,
            'admin_username': admin_username,
        }
        return jsonify(response), 200
    else:
        print(admin)
        response = {'message': 'Invalid username or password'}
        return jsonify(response), 401

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

        token_payload = {
            'user_id': user_id,
            'full_name': full_name,
            'points' : points,
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        token = jwt.encode(token_payload, secret_key, algorithm='HS256')
        
        # decoded = jwt.decode(token, algorithms='HS256',verify=True, key= secret_key)

        response = {
            'message': 'Login successful',
            'user_id': user_id,
            'full_name': full_name,
            'points' : points,
            'access_token' : token
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

@app.route("/reset-pass", methods = ['POST'])
def reset_pw():
    data = request.json
    username = data.get('username')
    new_pass = data.get('password')

    hashed_new_pass = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
    stored_new_pass = hashed_new_pass.decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE username = %s
            """,
            (stored_new_pass, username)
        )
        if cursor.rowcount == 0:
            response = {'message': 'Username not found'}
            return jsonify(response), 404
        
        conn.commit()
        response = {'message': 'Reset Password succesfully'}
        return jsonify(response), 201
    except:
        conn.rollback()
        response = {'message': 'Reset Password failed'}
        return jsonify(response), 500
    finally:
        pass

@app.route('/user-details', methods=['GET'])
def user_details():
    token = request.headers.get('Authorization')
    print(token)

    if token:
        try:
            payload = jwt.decode(token.split()[1], secret_key, algorithms=['HS256'])

            print(payload)

            user_id = payload['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, full_name, points
                FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()

            if user:
                user_id, full_name, points = user[0], user[1], user[2]
                response = {
                    'user_id': user_id,
                    'full_name': full_name,
                    'points': points
                }
                return jsonify(response), 200
            else:
                return jsonify({'message': 'User not found'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 402
    else:
        return jsonify({'message': 'Token is missing'}), 402
    
@app.route('/get-barang', methods=['GET'])
def exchangeable_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM barang_tukar")
        barang = cursor.fetchall()

        barang_list = []
        for barang in barang:
            barang_data = {
                'barang_id': barang[0],
                'barang_name': barang[1],
                'barang_points': barang[2],
                'barang_stok': barang[3],
                'barang_image':barang[4]
            }
            barang_list.append(barang_data)

        conn.close()

        return jsonify(barang_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        user_list = []
        for user in users:
            user_data = {
                'user_id': user[0],
                'full_name': user[1],
                'username': user[2],
                'email': user[3],
                'points': user[4],
            }
            user_list.append(user_data)

        conn.close()

        return jsonify(user_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    user_id = data.get('user_id')  # Fetch the user ID to delete

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        conn.commit()
        conn.close()

        response = {'message': 'User deleted successfully'}
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get-sampah', methods=['GET'])
def get_sampah():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sampah ORDER BY id_sampah  ASC")
        sampah = cursor.fetchall()

        sampah_list = []
        for sampah in sampah:
            sampah_data = {
                'id_sampah': sampah[0],
                'nama_sampah': sampah[1],
                'ukuran': sampah[2],
                'poin_sampah': sampah[3],
            }
            sampah_list.append(sampah_data)

        conn.close()

        return jsonify(sampah_list), 200

    except Exception as e:
        print(f"Error in get_sampah: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/update-stok', methods=['POST'])
def update_stok():
    data = request.json
    barang_id = data.get('barang_id') 
    barang_stok = data.get('barang_stok')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE barang_tukar
            SET barang_stok = %s
            WHERE barang_id = %s
            """,
            (barang_stok,barang_id)
        )

        conn.commit()
        conn.close()

        response = {'message': 'User deleted successfully'}
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/store-transaction', methods=['POST'])
def store_transaction():
    data = request.json
    user_id = data.get('user_id')
    jumlah_botol = data.get('jumlah_botol')
    jumlah_poin = data.get('jumlah_poin')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Store the transaction in the database
        cursor.execute(
            """
            INSERT INTO transaksi_ubah_botol (user_id, jumlah_botol, jumlah_poin)
            VALUES (%s, %s, %s)
            """,
            (user_id, jumlah_botol, jumlah_poin)
        )
        conn.commit()
        conn.close()
        response = {'message': 'Transaction stored successfully'}
        return jsonify(response), 200

    except Exception as e:
        print(f"Error in store_transaction: {str(e)}")
        traceback.print_exc()
        conn.rollback()
        response = {'message': 'Failed to store transaction'}
        return jsonify(response), 500

@app.route('/update-points', methods=['POST'])
def update_points():
    data = request.json
    user_id = data.get('user_id')
    points_to_add = data.get('points')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET points = points + %s
            WHERE user_id = %s
            """,
            (points_to_add, user_id)
        )
        conn.commit()
        response = {'message': 'Points updated successfully'}
        return jsonify(response), 200
    except:
        conn.rollback()
        response = {'message': 'Failed to update points'}
        return jsonify(response), 500
    finally:
        conn.close()

@app.route('/get-notifications', methods=['GET'])
def get_notifications():
    try:
        user_id = request.args.get('user_id', type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id_t_botol, jumlah_botol, jumlah_poin, tanggal
            FROM transaksi_ubah_botol
            WHERE user_id = %s
            ORDER BY tanggal DESC
            """,
            (user_id,)
        )

        notifications_botol = cursor.fetchall()

        cursor.execute(
            """
            SELECT id_t_poin, nama_barang, jumlah_poin, tanggal, user_id, barang_id, status
            FROM transaksi_tukar_point
            WHERE user_id = %s
            ORDER BY tanggal DESC
            """,
            (user_id,)
        )

        notifications_point = cursor.fetchall()

        notification_list = []
        for notification in notifications_botol:
            notification_data = {
                'id_t_botol': notification[0],
                'type': 'Setor Botol',
                'jumlah_botol': notification[1],
                'jumlah_poin': notification[2],
                'tanggal': notification[3].isoformat(),  # Convert datetime to ISO format
            }
            notification_list.append(notification_data)
        
        for notification in notifications_point:
            notification_data = {
                'id_t_poin': notification[0],
                'type': 'Tukar Poin',
                'nama_barang' : notification[1],
                'jumlah_point': notification[2],
                'tanggal': notification[3].isoformat(),
                'user_id': notification[4],
                'barang_id': notification[5],
                'status': notification[6],
            }
            notification_list.append(notification_data)

        notification_list.sort(key=lambda x: x['tanggal'], reverse=True)

        conn.close()

        return jsonify(notification_list), 200

    except Exception as e:
        print(f"Error in get_notifications: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/store-exchange-evidence', methods=['POST'])
def store_exchange_evidence():
    data = request.json
    user_id = data.get('user_id')
    barang_id = data.get('barang_id')
    total_points = data.get('total_points')
    exchange_date = data.get('exchange_date')
    barang_name = data.get('barang_name')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transaksi_tukar_point (nama_barang ,jumlah_poin, tanggal, user_id, barang_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (barang_name, total_points, exchange_date, user_id, barang_id)
        )
        conn.commit()
        conn.close()
        response = {'message': 'Exchange evidence stored successfully'}
        return jsonify(response), 200

    except Exception as e:
        print(f"Error in store_exchange_evidence: {str(e)}")
        traceback.print_exc()
        conn.rollback()
        response = {'message': 'Failed to store exchange evidence'}
        return jsonify(response), 500

if __name__ ==  '__main__':
    app.run(debug=True, host='0.0.0.0')
