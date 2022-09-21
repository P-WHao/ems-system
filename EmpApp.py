from flask import Flask, render_template, request
from pymysql import connections
from datetime import datetime
import os
import boto3
from config import *
# from django.http import HttpResponse

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

# ADD EMPLOYEE DONE


@app.route("/addemp/", methods=['GET', 'POST'])
def addEmp():
    return render_template("AddEmployee.html")

# EMPLOYEE OUTPUT


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

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (emp_id, first_name,
                                    last_name, gmail, phone_number, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.png"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

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
    return render_template('OutAddEmployee.html', name=emp_name)

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
    # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    cursor = db_conn.cursor()

    # response = s3bucket_getfile("https://s3.console.aws.amazon.com/s3/buckets/phoonwenhao-employee?region=us-east-1&tab=objects")

    try:
        cursor.execute(select_stmt, {'emp_id': int(emp_id)})
        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("OutEmployee.html", result=result) 
    # , response=response

# # Get Image From S3
# def s3bucket_getfile(file_path):
#     s3 = boto3.resource('s3')

#     obj = s3.Object(custombucket, file_path)

#     try:

#         file_stream = obj.get()['Body'].read()

#         if "png" in file_path:
#             response = HttpResponse(file_stream, content_type="image/jpeg")

#         response['Content-Disposition'] = 'filename=%s' % file_path

#         return response
#     except:
#         return False

# Delete Employee DONE


@app.route("/delemp/")
def delEmp():
    # Get Employee
    emp_id = "12"
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    delete_stmt = "DELETE * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(delete_stmt, {'emp_id': int(emp_id)})

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('OutRemoveEmployee.html')

# RMB TO CHANGE PORT NUMBER
if __name__ == '__main__':
    # or setting host to '0.0.0.0'
    app.run(host='0.0.0.0', port=80, debug=True)
