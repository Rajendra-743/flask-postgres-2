import psycopg2

# Establish a connection to your PostgreSQL database
conn = psycopg2.connect(
    dbname="clein",
    user="ganesa",
    password="ganesaganteng123.",
    host="localhost",
    port="5432"
)

# Open the image file and read its content as binary
with open('C:\\src\\clein_apps\\assets\\minyak_goreng.jpeg', 'rb') as f:
    image_data = f.read()

# Use the lo_create and lo_put functions
with conn.cursor() as cur:
    cur.execute("SELECT lo_create(0)")  # Creates a new Large Object and gets its OID
    oid = cur.fetchone()[0]

    cur.execute("SELECT lo_put(%s, 0, %s)", (oid, psycopg2.Binary(image_data)))  # Writes image data to the Large Object
    conn.commit()

conn.close()
