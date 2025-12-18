from flask import Flask, request
import pymysql
import time

app = Flask(__name__)

def get_connection():
    for _ in range(20):
        try:
            return pymysql.connect(
                user="cvuser",
                password="cvpass",
                host="mariadb",
                port=3306,
                database="cv",
                connect_timeout=5
            )
        except pymysql.OperationalError:
            time.sleep(3)

    raise Exception("MariaDB is not reachable after multiple retries")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INT PRIMARY KEY,
            views INT
        )
    """)

    cur.execute("""
        INSERT IGNORE INTO counter (id, views)
        VALUES (1, 0)
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/view")
def view_counter():
    conn = get_connection()
    cur = conn.cursor()

    read = request.args.get("read")

    if read == "true":
        cur.execute("SELECT views FROM counter WHERE id=1")
        result = cur.fetchone()
        conn.close()
        return str(result[0])

    cur.execute("UPDATE counter SET views = views + 1 WHERE id=1")
    conn.commit()

    cur.execute("SELECT views FROM counter WHERE id=1")
    result = cur.fetchone()
    conn.close()

    return str(result[0])

init_db()
app.run(host="0.0.0.0", port=5000)

