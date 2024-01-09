from flask import Flask, request, redirect, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split as ttsplit
from sklearn import svm
import pandas as pd
import pickle
import numpy as np
from datetime import datetime
from flask import Flask, render_template, redirect, request, session
from flask import Flask, render_template
import firebase_admin
import random
from firebase_admin import credentials
import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1 import FieldFilter
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from pdfquery import PDFQuery, pdfquery
import PyPDF2
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/'
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key="ScannedPrescription@1234"
app.config['upload_folder']='/static/upload'

def combinePdfs(filename1, filename2, filename3, result_filename):
    pdfFiles = []
    root = os.getcwd()
    if(filename1):
        pdfFiles.append(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    if (filename2):
        pdfFiles.append(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    if (filename3):
        pdfFiles.append(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
    pdfFiles.sort(key=str.lower)
    print("Pdf Files : \n", pdfFiles)
    pdfWriter = PyPDF2.PdfWriter()
    for filename in pdfFiles:
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        for pageNum in range(0, len(pdfReader.pages)):
            pageObj = pdfReader.pages[pageNum]
            pdfWriter.add_page(pageObj)
    pdfOutput = open(os.path.join(app.config['UPLOAD_FOLDER'], result_filename), 'wb')
    pdfWriter.write(pdfOutput)
    pdfOutput.close()
    print("PDF Created Success")

def readPdf(filename):
    pdfFileObj = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb')
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    # printing number of pages in pdf file
    print(len(pdfReader.pages))
    # creating a page object
    pageObj = pdfReader.pages[0]
    # extracting text from page
    data = pageObj.extract_text()
    # closing the pdf file object
    pdfFileObj.close()
    return data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/newuser", methods=["POST","GET"])
def newuser():
    try:
        msg=""
        print("Add New User page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname, 'LastName': lname,
                    'UserName': uname, 'Password': pwd,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newuser')
            id = json['id']
            newuser_ref.document(id).set(json)
            print("New User Inserted Success")
            msg = "New User Added Success"
        return render_template("newuser.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route("/adminlogin", methods=["POST","GET"])
def adminlogin():
    msg=""
    if(request.method=="POST"):
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        if(uname=="admin" and pwd=="admin"):
            return render_template("adminmainpage.html")
        else:
            msg="Invalid UserName/Password"
    return render_template("adminlogin.html", msg=msg)

@app.route("/logout")
def logout():
    return render_template("index.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/stafflogin")
def stafflogin():
    return render_template("stafflogin.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/adminaddstaff", methods=["POST","GET"])
def adminaddstaff():
    try:
        print("Add New Staff page")
        msg=""
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname, 'LastName': lname,
                    'UserName': uname, 'Password': pwd,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newuser')
            id = json['id']
            newuser_ref.document(id).set(json)
        return render_template("adminaddstaff.html", msg=msg)
    except Exception as e:
        return render_template("adminaddstaff.html", msg=str(e))

@app.route('/userlogincheck', methods=['POST'])
def userlogincheck():
    try:
        msg=""
        if request.method == 'POST':
            uname = request.form['uname']
            pwd = request.form['pwd']
            db = firestore.client()
            print("Uname : ", uname, " Pwd : ", pwd);
            newdb_ref = db.collection('newuser')
            dbdata = newdb_ref.get()
            data = []
            flag = False
            for doc in dbdata:
                #print(doc.to_dict())
                #print(f'{doc.id} => {doc.to_dict()}')
                #data.append(doc.to_dict())
                data = doc.to_dict()
                if(data['UserName']==uname and data['Password']==pwd):
                    flag=True
                    session['userid']=data['id']
                    break
            if(flag):
                print("Login Success")
                return render_template("usermainpage.html")
            else:
                return render_template("userlogin.html", msg="UserName/Password is Invalid")
        else:
            return render_template("userlogin.html", msg=msg)
    except Exception as e:
        return render_template("userlogin.html", msg=e)

@app.route("/adminviewstaffs")
def adminviewstaffs():
    try:
        db = firestore.client()
        newstaff_ref = db.collection('newstaff')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Staff Data ", data)
        return render_template("adminviewstaffs.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewcontacts")
def adminviewcontacts():
    try:
        db = firestore.client()
        newstaff_ref = db.collection('newcontact')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            data.append(doc.to_dict())
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewusers")
def adminviewusers():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Users Data ", data)
        return render_template("adminviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewreports")
def adminviewreports():
    try:
        db = firestore.client()
        newstaff_ref = db.collection('newprescription')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            data.append(doc.to_dict())
        return render_template("adminviewreports.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/userupdateprescription",methods=['POST','GET'])
def userupdateprescription():
    msg = ""
    if request.method == 'POST':
        userid = session['userid']
        hname = request.form['hname']
        dname = request.form['dname']
        reason = request.form['reason']
        comments = request.form['comments']
        id = str(random.randint(1000, 9999))
        print("Insert Prescription")
        file1 = request.files['file1']
        file2 = request.files['file2']
        file3 = request.files['file3']
        filename1 = None
        filename2 = None
        filename3 = None
        result_filename='Result_Filename'+ str(id) + ".pdf"
        if file1.filename == '':
            return redirect(request.url)
        if file1:
            filename1 = "File1" + str(id) + ".pdf"
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        if file2:
            filename2 = "File2" + str(id) + ".pdf"
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        if file3:
            filename3 = "File3" + str(id) + ".pdf"
            file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
        json = {'id': id, 'UserId':userid,
                'HospitalName': hname, 'DoctorName': dname,
                'Comments': comments, 'Reason': reason,
                'File1': filename1, 'File2': filename2,
                'File3': filename3, 'Result_Filename':result_filename}
        combinePdfs(filename1, filename2, filename3, result_filename)
        #print("JSON : ",json)
        db = firestore.client()
        newuser_ref = db.collection('newprescription')
        id = json['id']
        newuser_ref.document(id).set(json)
        msg="Prescription Uploaded Success"
        return render_template("userupdateprescription.html", msg=msg)
    else:
        return render_template("userupdateprescription.html",msg=msg)

@app.route("/userviewprofile")
def userviewprofile():
    try:
        userid = session['userid']
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = {}
        for doc in userdata:
            temp =  doc.to_dict()
            print(f'{doc.id} => {doc.to_dict()}')
            if(temp['id']==userid):
                data = doc.to_dict()
                break
        return render_template("userviewprofile.html", row=data)
    except Exception as e:
        return str(e)

@app.route("/usercheckbehaviour")
def usercheckbehaviour():
    return render_template("usercheckbehaviour.html")

@app.route("/userviewreports")
def userviewreports():
    return render_template("userviewreports.html")


@app.route("/userviewprescriptions")
def userviewprescriptions():
    try:
        userid = session['userid']
        db = firestore.client()
        newstaff_ref = db.collection('newprescription')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            if(doc.to_dict()['UserId']==userid):
                data.append(doc.to_dict())
        print("Staff Data ", data)
        return render_template("userviewprescriptions.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/userviewdetails",methods=['POST','GET'])
def userviewdetails():
    try:
        args = request.args
        filename = args['filename']
        data=readPdf(filename)
        print(data)
        return render_template("userviewdetails.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewdetails",methods=['POST','GET'])
def adminviewdetails():
    try:
        args = request.args
        filename = args['filename']
        data=readPdf(filename)
        print(data)
        return render_template("adminviewdetails.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/contact",methods=["POST","GET"])
def contact():
    try:
        print("Add New Staff page")
        msg=""
        if request.method == 'POST':
            cname = request.form['cname']
            message = request.form['message']
            email = request.form['email']
            phnum = request.form['phnum']
            id = str(random.randint(1000, 9999))
            json = {'id': id,'ContactName': cname,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Message': message}
            db = firestore.client()
            db_ref = db.collection('newcontact')
            db_ref.document(id).set(json)
            msg="Contact Added Success"
        return render_template("contact.html", msg=msg)
    except Exception as e:
        return render_template("contact.html", msg=str(e))

if __name__ == '__main__':
    app.run(debug=True)