import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def connect_db(db_name=None):

    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=db_name
        )
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    
def create_database():
    conn = connect_db(None)
    if conn:
        try:
            db_name = os.getenv("DB_NAME")
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute("CREATE DATABASE student_management;")
                print("Database 'student_management' created successfully.")
            else:
                print("Database 'student_management' already exists.")
        except Exception as e:
            print(f"Error creating database: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


def create_tables():

    conn = connect_db("student_management")
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(100)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(100)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_teacher (
                    student_id INT REFERENCES students(student_id),
                    teacher_id INT REFERENCES teachers(teacher_id),
                    PRIMARY KEY (student_id, teacher_id)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_log (
                    log_id SERIAL PRIMARY KEY,
                    user_id INT,
                    user_name VARCHAR(100),
                    user_type VARCHAR(50),  -- "student" or "teacher"
                    sign_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
