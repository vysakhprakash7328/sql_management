from database_conn import connect_db, create_database, create_tables
from datetime import datetime


def create_user(user_type, name, email, password):
    if user_type not in ["student", "teacher"]:
        print("Invalid user type. Use 'student' or 'teacher'.")
        return None

    table = "students" if user_type == "student" else "teachers"
    id_column = "student_id" if user_type == "student" else "teacher_id"
    
    conn = connect_db("student_management")
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {table} (name, email, password)
                VALUES (%s, %s, %s) RETURNING {id_column}
            """, (name, email, password))
            
            user_id = cursor.fetchone()[0]
            
            conn.commit()
            print(f"{user_type.capitalize()} created successfully with ID: {user_id}.")
            return user_id
        
        except Exception as e:
            print(f"Error creating {user_type}: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
            
            

                


def log_user_sign_in(user_id, user_name, user_type):

    conn = connect_db("student_management")
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

def authenticate_user(email, password, user_type):

    if user_type not in ["student", "teacher"]:
        print("Invalid user type. Use 'student' or 'teacher'.")
        return None
    
    table = "students" if user_type == "student" else "teachers"
    conn = connect_db("student_management")
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
                    print(f"Login successful for {user_type.capitalize()} {user_name}.")
                    
                    log_user_sign_in(user_id, user_name, user_type)
                    
                    print(f"{user_type} with {user_id} login successfully")
                else:
                    print("Incorrect password.")
                    return None
            else:
                print(f"No {user_type} found with this email.")
                return None
        except Exception as e:
            print(f"Error during authentication: {e}")
        finally:
            cursor.close()
            conn.close()
    return None


def associate_teacher_to_student(student_id, teacher_id):

    conn = connect_db("student_management")
    if conn:
        try:
            cursor = conn.cursor()
            if student_id is None or teacher_id is None:
                print("Cannot assign: student_id or teacher_id is None.")
                return
            
            cursor.execute("""
                INSERT INTO student_teacher (student_id, teacher_id)
                VALUES (%s, %s)
            """, (student_id, teacher_id))
            
            conn.commit()
            print(f"Student ID {student_id} is now associated with Teacher ID {teacher_id}.")
        except Exception as e:
            print(f"Error associating student to teacher: {e}")
        finally:
            cursor.close()
            conn.close()
            



def update_student(student_id, name=None, email=None, password=None):
    conn = connect_db("student_management")
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
                print("No fields to update.")
                return None
            
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(fields)} WHERE student_id = %s RETURNING student_id"
            cursor.execute(query, values)
            
            updated_student_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"Student with ID {updated_student_id} updated successfully.")
            return updated_student_id
        
        except Exception as e:
            print(f"Error updating student: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
            
def delete_student(student_id):
    conn = connect_db("student_management")
    if conn:
        try:
            cursor = conn.cursor()
 
            
            query = "DELETE from students where student_id = %s RETURNING student_id"
            cursor.execute(query, student_id)
            
            deleted_student_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"Student with ID {deleted_student_id} deleted successfully.")
            return deleted_student_id
        
        except Exception as e:
            print(f"Error updating student: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    
def get_associated_teachers(student_id):

    conn = connect_db("student_management")
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
            print(f"Student {student_id} is associated with the following teachers:")
            for teacher in teachers:
                print(f"- {teacher[0]} (Email: {teacher[1]})")
        
        except Exception as e:
            print(f"Error fetching associated teachers: {e}")
        finally:
            cursor.close()
            conn.close()
            
def get_all_students():
    conn = connect_db("student_management")
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * from students")
            students = cursor.fetchall()
            print("List of all students")
            for student in students:
                print(student[0], student[1], student[2])
        except Exception as e:
            print(f"Error fetching students list: {e}")
        finally:
            cursor.close()
            conn.close()
def main():
    create_database()
    create_tables()

    teacher_1_id = create_user("teacher", "John Doe", "john.doe@example.com", "password123")
    teacher_2_id = create_user("teacher", "Alice Brown", "alice.brown@example.com", "password123")
    teacher_3_id = create_user("teacher", "Michael Green", "michael.green@example.com", "password123")

    student_1_id = create_user("student", "Jane Smith", "jane.smith@example.com", "password123")
    student_2_id = create_user("student", "Emily White", "emily.white@example.com", "password123")

    
    associate_teacher_to_student(student_id=student_1_id, teacher_id=teacher_1_id)
    associate_teacher_to_student(student_id=student_1_id, teacher_id=teacher_2_id)
    associate_teacher_to_student(student_id=student_2_id, teacher_id=teacher_2_id)
    associate_teacher_to_student(student_id=student_2_id, teacher_id=teacher_3_id)

    
    authenticate_user("jane.smith@example.com", "password123", "student")
    authenticate_user("alice.brown@example.com", "password123", "teacher")
    
        
    get_all_students()
    
    get_associated_teachers(student_2_id)


    
if __name__ == "__main__":
    main()
