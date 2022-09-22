from curses import flash
from flask import Flask, render_template, request
from pymysql import connections
import pymysql
from datetime import datetime
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

# MAIN PAGE


@app.route("/")
def home():
    return render_template("Homepage.html")

# ADD EMPLOYEE


@app.route("/addemp/", methods=['GET', 'POST'])
def addEmp():
    return render_template("AddEmployee.html")

# ADD EMPLOYEE OUTPUT (DISPLAY MESSAGE)


@app.route("/addemp/results", methods=['GET', 'POST'])
def Emp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gmail = request.form['gmail']
    phone_number = request.form['phone_number']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT IGNORE INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        returnQuery = cursor.execute(insert_sql, (emp_id, first_name,
                                                  last_name, gmail, phone_number, pri_skill, location))
        db_conn.commit()
        # return 0 is not added, 1 is added
        print(returnQuery)
        emp_name = "" + first_name + " " + last_name

        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "employee-image/emp-id-" + str(emp_id) + "_image_file.png"
        s3 = boto3.resource('s3')

        try:
            if returnQuery == 1:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                # Display System Message
                flash('Employee Added Successfully')

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    if returnQuery == 1:
        return render_template('AddEmployeeOut.html', name=emp_name)
    else:
        return render_template('AddEmployeeOutFail.html', id=emp_id)


# Get Employee DONE


@app.route("/getemp/")
def getEmp():
    return render_template('SearchEmployee.html')

# Get Employee Results


@app.route("/getemp/results", methods=['GET', 'POST'])
def Employee():
    # Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    key = "employee-image/emp-id-" + str(emp_id) + "_image_file.png"

    url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)

    try:
        returnResp = cursor.execute(select_stmt, {'emp_id': int(emp_id)})
        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    if returnResp == 1:
        return render_template("SearchEmployeeOut.html", result=result, url=url)
    else:
        return render_template('SearchEmployeeOutFail.html', id=emp_id)
    

# Delete Employee DONE


@app.route("/delemp/", methods=['GET', 'POST'])
def delEmp():
    # Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    delete_stmt = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
    cursor1 = db_conn.cursor()

    try:
        cursor.execute(select_stmt, {'emp_id': int(emp_id)})
        cursor1.execute(delete_stmt, {'emp_id': int(emp_id)})
        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        return str(e)

    finally:
        cursor.close()
        cursor1.close()

    return render_template('RemoveEmployeeOut.html', result=result)


# Display all Employee in Table
@app.route('/displayallemp/')
def displayAllEmp():
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT * FROM employee"
    cursor = db_conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(select_stmt)
    data = cursor.fetchall()
    cursor.close()
    return render_template('DisplayAllEmployee.html', employee=data)


# Edit Employee Details
@app.route('/diseditemp/', methods=['GET', 'POST'])
def disEditEmp():
    # Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_stmt, {'emp_id': int(emp_id)})
        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("EditEmployee.html", result=result)


# Edit Employee Details
@app.route('/diseditemp/edit<id>', methods=['GET', 'POST'])
def disEditAEmp(id):
    # Get Employee
    # emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gmail = request.form['gmail']
    phone_number = request.form['phone_number']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, gmail = %s, phone_number = %s, pri_skill = %s, location = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (first_name, last_name, gmail, phone_number, pri_skill, location, id))
        db_conn.commit()
        
        emp_name = "" + first_name + " " + last_name

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('EditEmployeeOut.html', name=emp_name)

# RMB TO CHANGE PORT NUMBER
if __name__ == '__main__':
    # or setting host to '0.0.0.0'
    app.run(host='0.0.0.0', port=80, debug=True)
