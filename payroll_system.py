from faker import Faker
import mysql.connector
import random
from flask import Flask, render_template, request

# Establish connection to MySQL database
cnx = mysql.connector.connect(
    host="localhost",
    user="ysl",
    password="ysl@123",
    database="payroll_system"
)

# Create a cursor to execute SQL queries
cursor = cnx.cursor()

# Create a Faker instance
fake = Faker()

# Generate fake employee details
employee_count = 100  # Number of employees to generate
employees = []

for _ in range(employee_count):
    employee = {
        "employee_id": fake.random_int(min=1000, max=9999),
        "name": fake.name(),
        "position": fake.job(),
        "department": fake.company_suffix()
    }
    employees.append(employee)

# Insert employee details into the database
for employee in employees:
    # Check if the employee ID already exists in the database
    query = "SELECT COUNT(*) FROM employees WHERE employee_id = %s"
    cursor.execute(query, (employee["employee_id"],))
    result = cursor.fetchone()

    if result is None or result[0] == 0:
        insert_employee_query = "INSERT INTO employees (employee_id, name, position, department) VALUES (%s, %s, %s, %s)"
        employee_values = (employee["employee_id"], employee["name"],
                           employee["position"], employee["department"])
        cursor.execute(insert_employee_query, employee_values)

# Generate fake salary data and insert into the database
for employee in employees:
    salary = random.randint(3000, 10000)
    insert_salary_query = "INSERT INTO salaries (employee_id, amount) VALUES (%s, %s)"
    salary_values = (employee["employee_id"], salary)
    cursor.execute(insert_salary_query, salary_values)

# Generate fake attendance data and insert into the database
for employee in employees:
    for _ in range(30):  # Assuming 30 days of attendance
        hours_worked = random.randint(4, 10)
        insert_attendance_query = "INSERT INTO attendance (employee_id, hours_worked) VALUES (%s, %s)"
        attendance_values = (employee["employee_id"], hours_worked)
        cursor.execute(insert_attendance_query, attendance_values)

# Commit the changes and close the connection
cnx.commit()
cursor.close()
cnx.close()

# Create a Flask web application
app = Flask(__name__)

# Define a route to display employee information


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/employee', methods=['POST'])
def display_employee():
    employee_id = request.form['employee_id']

    # Connect to the MySQL database
    cnx = mysql.connector.connect(
        host="localhost",
        user="ysl",
        password="ysl@123",
        database="payroll_system"
    )
    cursor = cnx.cursor()

    # Retrieve employee information from the database
    query = "SELECT * FROM employees WHERE employee_id = %s"
    cursor.execute(query, (employee_id,))
    employee = cursor.fetchone()

    if employee:
        # Retrieve salary information from the database
        query = "SELECT SUM(amount) FROM salaries WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        total_salary = cursor.fetchone()[0]

        # Retrieve attendance information from the database
        query = "SELECT SUM(hours_worked) FROM attendance WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        total_hours_worked = cursor.fetchone()[0]

        # Calculate the salary for the hours worked
        if total_hours_worked:
            salary_per_hour = total_salary / total_hours_worked
        else:
            salary_per_hour = 0

        # Calculate the total salary income
        query = "SELECT SUM(amount) FROM salaries"
        cursor.execute(query)
        total_salary_income = cursor.fetchone()[0]

        # Render the employee information template with the calculated values
        return render_template('employee.html', employee=employee, total_hours_worked=total_hours_worked, salary_per_hour=salary_per_hour, total_salary_income=total_salary_income)
    else:
        # Render a template for employee not found
        return render_template('not_found.html', employee_id=employee_id)

    # Close the connection
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    app.run(debug=True)
