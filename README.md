# Student Database CRUD Application

A small Python application that connects to a PostgreSQL database and performs
the four CRUD operations (Create, Read, Update, Delete) on a `students` table.

**Demo video:** PASTE_YOUR_VIDEO_LINK_HERE

## Project structure

```
students-crud-app/
├── README.md
├── requirements.txt
├── database/
│   ├── 01_create_database.sql      creates the students_db database
│   └── 02_schema_and_data.sql      creates the students table and inserts the initial data
└── src/
    └── app.py                      the application
```

## Database schema

Table `students`:

| Field           | Type and constraints                  |
|-----------------|---------------------------------------|
| student_id      | Integer, primary key, auto-increment  |
| first_name      | Text, not null                        |
| last_name       | Text, not null                        |
| email           | Text, not null, unique                |
| enrollment_date | Date                                  |

## Requirements

- PostgreSQL (tested with PostgreSQL 18) and pgAdmin 4
- Python 3.9 or newer
- The `psycopg2-binary` package

## Setup

1. **Install the Python dependency**

   ```
   pip install -r requirements.txt
   ```

2. **Create the database.** In pgAdmin 4, right-click **Databases**, choose
   **Create > Database**, name it `students_db`, and save. (Or run the single
   statement in `database/01_create_database.sql` by itself.)

3. **Create the table and load the initial data.** In pgAdmin, right-click
   `students_db`, open the **Query Tool**, paste the contents of
   `database/02_schema_and_data.sql`, and run it. You can run this script again
   at any time to reset the table to the initial three students.

## How to run

There is no compile step. From the project folder, run:

```
python src/app.py
```

The program asks for your PostgreSQL password (typing is hidden), then shows a
menu:

```
1. Show all students
2. Add a student
3. Update a student's email
4. Delete a student
5. Exit
```

### Optional configuration

By default the app connects to `localhost:5432`, database `students_db`, user
`postgres`. You can change any of these with environment variables
(`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

Windows PowerShell example:

```
$env:DB_PASSWORD = "your_password"
python src/app.py
```

## Functions (in `src/app.py`)

| Function | What it does |
|----------|--------------|
| `getAllStudents()` | Retrieves every record from the `students` table and prints it as a table. |
| `addStudent(first_name, last_name, email, enrollment_date)` | Inserts a new student (date format `YYYY-MM-DD`) and returns the new `student_id`. |
| `updateStudentEmail(student_id, new_email)` | Changes the email of the student with that `student_id`. |
| `deleteStudent(student_id)` | Deletes the student with that `student_id`. |

Error handling: duplicate emails, invalid dates, missing required values, and
unknown student IDs are reported with a clear message instead of crashing, and
a failed operation is rolled back so the database is never left half-changed.

## Checking the results in pgAdmin

After adding, updating, or deleting a student, run this in the pgAdmin Query
Tool to see the change:

```sql
SELECT * FROM students ORDER BY student_id;
```
