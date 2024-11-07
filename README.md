*** Student Management Application ***


This is a simple Flask-based application for managing student and teacher data, along with assigning teachers to students and providing basic authentication for users. The application connects to a PostgreSQL database and provides API endpoints for performing CRUD operations on student and teacher data.

*** Features ***

1. Create and authenticate users (students and teachers).
2. Assign teachers to students.
3. Update and delete student records.
4. Retrieve lists of all students and teachers.
5. Fetch the list of teachers assigned to a student.
6. Prerequisites
7. To run this application locally, you will need:


*** Installation ***

1. Clone the Repository
    git clone https://github.com/your-username/student-management-flask.git
    cd student-management-flask
2. Create a Virtual Environment (Optional)
    It's recommended to create a virtual environment to manage dependencies:

    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
    Install the required dependencies from the requirements.txt file:

    pip install -r requirements.txt

4. Configure Database Connection
    Update the .env file with your PostgreSQL database credentials (username, password, host, port).

5. PostgreSQL Database and tables
    Database and tables will be created at the time of first request


6. Run the Flask Application
Start the Flask development server:

python app.py
The application will be available at http://localhost:5000/.

*** API Endpoints ***
1. *** Create User (POST /create_user) ***
    Creates a new student or teacher.

    make sure user_type is student or teacher

    Sample Request Body:
    json
    {
        "user_type": "student",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "password123"
    }
    Response:
    json
    
    {
        "message": "Student created successfully.",
        "user_id": 1
    }
2. ***Authenticate User (POST /authenticate)***
    Authenticates a user based on email and password.

    Sample Request Body:
    json
    
    {
        "email": "john.doe@example.com",
        "password": "password123",
        "user_type": "student"
    }
    Response:
    json
    
    {
        "student with ID 1 login successfully": 200
    }
3. ***Assign Teacher to Student (POST /assign_teacher_to_student)***
    Assigns a teacher to a student.

    Sample Request Body:
    json
    
    {
        "student_id": 1,
        "teacher_id": 2
    }
    Response:
    json
    
    {
        "message": "Student ID 1 is now associated with Teacher ID 2."
    }
4. ***Update Student (PUT /update_student)***
    Updates a student's information.

    Sample Request Body:
    json

    {
        "student_id": 1,
        "name": "Updated Name",
        "email": "updated.email@example.com"
    }
    Response:
    json
    {
        "message": "Student with ID 1 updated successfully."
    }
5. ***Delete Student (DELETE /delete_student)***
    sample Deletes a student record.

    Request Body:
    json
    {
        "student_id": 1
    }
    Response:
    json
    
    {
        "message": "Student with ID 1 deleted successfully."
}
6. ***Get All Students (GET /get_all_students)***
    Retrieves a list of all students.

    Response:
    json
    
    {
        "students": [
            {"student_id": 1, "name": "John Doe", "email": "john.doe@example.com"},
            {"student_id": 2, "name": "Jane Smith", "email": "jane.smith@example.com"}
        ]
    }
7. ***Get Assigned Teachers (GET /get_assigned_teachers)***
    Retrieves a list of teachers assigned to a student.

    Request Parameters:
    student_id (e.g., 1)
    Response:
    json
    
    {
        "teachers": [
            {"name": "Teacher A", "email": "teacher.a@example.com"},
            {"name": "Teacher B", "email": "teacher.b@example.com"}
        ]
    }
    Error Handling
    If any error occurs, the API will return a 400 or 500 status code with an error message. For example:

    json
    
    {
        "error": "Error fetching students list: <error_message>"
    }
***Testing the API***

You can test the API endpoints using tools like Postman or curl.

For example, to test the GET /get_all_students endpoint using curl:

curl -X GET "http://localhost:5000/get_all_students"


***Acknowledgements***
Flask for creating the web application framework.
psycopg2 for PostgreSQL integration.
