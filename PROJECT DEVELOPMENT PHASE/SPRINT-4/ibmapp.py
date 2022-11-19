from flask import Flask,render_template,request,redirect, redirect, url_for, session
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import joblib

import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "zFHdtlYdOuhllotKkSiH7NTZqeJjt_o-j-B2hm0UGbWI"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


app=Flask(__name__)
cors=CORS(app)
model=pickle.load(open('Decision_Tree_Model.pkl','rb'))
 
mysql = MySQL(app)
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'avis@006600@siva'
app.config['MYSQL_DB'] = 'nalaithiran'






@app.route('/',methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('RegisterDetails.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 

 
@app.route('/reg', methods =['GET', 'POST'])
def reg():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('reg.html', msg = msg)

@app.route('/register')
def register():
    return render_template('RegisterDetails.html')


@app.route('/predict',methods=['GET' , 'POST'])
def predict():
    if request.method == "POST":
        name = request.form.get('name')
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        dependents = request.form.get('dependents')
        education = request.form.get('education')
        Self_Employed = request.form.get('Self_Employed')
        ApplicantIncome = request.form.get('ApplicantIncome')
        coapp_income = request.form.get('coapp_income')
        loan_amount = request.form.get('loan_amount')
        term = request.form.get('term')
        credit_history = request.form.get('credit_history')
        property_area = request.form.get('property_area')

        x = [[name,gender, marital_status, dependents, education, Self_Employed, ApplicantIncome, coapp_income, loan_amount, term, credit_history, property_area]]

        prediction=model.predict(pd.DataFrame(columns=['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Property_Area'],
                                data=np.array([gender, marital_status, dependents, education, Self_Employed, ApplicantIncome, coapp_income, loan_amount, term, credit_history, property_area]).reshape(1, 11)))
        

        payload_scoring = {"input_data": [{"field": [['gender', 'married', 'dependents', 'education', 'self_Employed', 'ApplicantIncome', 'coapp_income', 'loan_amount', 'term', 'credit_history', 'property_area']], "values": x}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/1aaee38b-270c-4f93-b30a-d14a3e5321ee/predictions?version=2022-11-18', json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})
        deprediction =response_scoring.json()

        print(deprediction)
        # pre = deprediction['deprediction'][0]['value'][0][0]
        # print("final prediction : ",pre)

        # print(prediction)

        if prediction == 1:
            pred = "Loan_Approved"
            return render_template('temp.html')
        else:
            pred = "Not_Approved"
            return render_template('notapproved.html')
    


if __name__=='__main__':
    app.run()







