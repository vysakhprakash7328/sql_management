from database_conn import connect_db, create_database, create_tables
from datetime import datetime
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


@app.before_request
def init_db():
    
    create_database()
    create_tables()
    
    
@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json()
    user_type = data.get("user_type")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if user_type not in ["student", "teacher"]:
        return jsonify({"error": "Invalid user type. Use 'student' or 'teacher'."}), 400

    table = "students" if user_type == "student" else "teachers"
    id_column = "student_id" if user_type == "student" else "teacher_id"
    
    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {table} (name, email, password)
                VALUES (%s, %s, %s) RETURNING {id_column}
            """, (name, email, password))
            
            user_id = cursor.fetchone()[0]
            
            conn.commit()
            return jsonify({"message": f"{user_type.capitalize()} created successfully.", "user_id": user_id}), 201
        
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Error creating {user_type}: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Failed to connect to the database."}), 500
    
    

def log_user_sign_in(user_id, user_name, user_type):

    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_log (user_id, user_name, user_type, sign_in_time)
                VALUES (%s, %s, %s, %s)
            """, (user_id, user_name, user_type, datetime.now()))
            
            conn.commit()
            print("User sign-in logged.")
        except Exception as e:
            print(f"Error logging sign-in: {e}")
        finally:
            cursor.close()
            conn.close()
            
@app.route("/authenticate", methods=["POST"])
def authenticate_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received."}), 400

    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type")

    if not all([email, password, user_type]):
        return jsonify({"error": "Missing email, password, or user_type."}), 400

    if user_type not in ["student", "teacher"]:
        return jsonify({"error": "Invalid user type. Use 'student' or 'teacher'."}), 400

    table = "students" if user_type == "student" else "teachers"
    conn = connect_db(os.getenv("DB_NAME"))

    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT {user_type}_id, name, email, password
                FROM {table}
                WHERE email = %s
            """, (email,))

            result = cursor.fetchone()

            if result:
                user_id, user_name, stored_email, stored_password = result
                
                if password == stored_password:
                    log_user_sign_in(user_id, user_name, user_type)
                    return jsonify({"message": f"{user_type.capitalize()} with ID {user_id} logged in successfully."}), 200
                else:
                    return jsonify({"error": "Incorrect password."}), 400
            else:
                return jsonify({"error": f"No {user_type} found with this email."}), 400
        except Exception as e:
            return jsonify({"error": f"Error during authentication: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Failed to connect to the database."}), 500


@app.route("/assign_teacher", methods=["POST"])
def assign_teacher_to_student():
    data = request.get_json()
    
    student_id = data.get("student_id")
    teacher_id = data.get("teacher_id")
    
    if not student_id or not teacher_id:
        return jsonify({"error": "student_id and teacher_id are required."}), 400

    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO student_teacher (student_id, teacher_id)
                VALUES (%s, %s)
            """, (student_id, teacher_id))

            conn.commit()

            return jsonify({"message": f"Student ID {student_id} is now associated with Teacher ID {teacher_id}."}), 200

        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Error associating student to teacher: {str(e)}"}), 500

        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Failed to connect to the database."}), 500

            



@app.route("/update_student", methods=["PUT"])
def update_student():
    data = request.get_json()
    
    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not student_id:
        return jsonify({"error": "student_id is required."}), 400

    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()
            
            fields = []
            values = []
            
            if name:
                fields.append("name = %s")
                values.append(name)
            if email:
                fields.append("email = %s")
                values.append(email)
            if password:
                fields.append("password = %s")
                values.append(password)
                
            if not fields:
                return jsonify({"error": "No fields to update."}), 400
            
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(fields)} WHERE student_id = %s"
            cursor.execute(query, values)
            
            conn.commit()
            
            return jsonify({"message": f"Student with ID {student_id} updated successfully."}), 200
        
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Error updating student: {str(e)}"}), 500
        
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Failed to connect to the database."}), 500

@app.route("/delete_student", methods=["DELETE"])
def delete_student():
    data = request.get_json()
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"error": "student_id is required."}), 400

    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM student_teacher WHERE student_id = %s", (student_id,))
            
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            
            conn.commit()
            
            return jsonify({"message": f"Student with ID {student_id} deleted successfully."}), 200

        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Error deleting student: {str(e)}"}), 500
        
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Failed to connect to the database."}), 500

    
@app.route("/get_assigned_teachers", methods=["GET"])
def get_assigned_teachers():
    student_id = request.args.get("student_id")

    if not student_id:
        return jsonify({"error": "student_id is required."}), 400

    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT teachers.name, teachers.email
                FROM teachers
                INNER JOIN student_teacher ON teachers.teacher_id = student_teacher.teacher_id
                WHERE student_teacher.student_id = %s
            """, (student_id,))

            teachers = cursor.fetchall()

            if teachers:
                teachers_list = [{"name": teacher[0], "email": teacher[1]} for teacher in teachers]
                return jsonify({"student_id": student_id, "teachers": teachers_list}), 200
            else:
                return jsonify({"message": f"No teachers assigned to student with ID {student_id}."}), 404

        except Exception as e:
            return jsonify({"error": f"Error fetching associated teachers: {str(e)}"}), 500

        finally:
            cursor.close()
            conn.close()

    return jsonify({"error": "Failed to connect to the database."}), 500


@app.route("/get_all_students", methods=["GET"])
def get_all_students():
    conn = connect_db(os.getenv("DB_NAME"))
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, name, email FROM students")
            
            students = cursor.fetchall()

            if students:
                students_list = [{"student_id": student[0], "name": student[1], "email": student[2]} for student in students]
                return jsonify({"students": students_list}), 200
            else:
                return jsonify({"message": "No students found."}), 404

        except Exception as e:
            return jsonify({"error": f"Error fetching students list: {str(e)}"}), 500

        finally:
            cursor.close()
            conn.close()

    return jsonify({"error": "Failed to connect to the database."}), 500


if __name__ == "__main__":
    app.run(debug=True)


