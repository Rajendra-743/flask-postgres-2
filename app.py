from flask import Flask
import psycopg2
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

@app.route('/')
def hello_world():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 'Hello, PostgreSQL!'")
    result = cursor.fetchone()[0]
    conn.close()
    return result

if __name__ ==  '__main__':
    app.run(debug=True)
