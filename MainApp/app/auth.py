from flask import Blueprint, session, request, redirect, url_for, render_template, flash
from . import db
from random import randint
from datetime import datetime, date
import time
auth = Blueprint('auth',__name__)


def generateUID(length=12):
    d = [str(i) for i in range(10)]
    d = d + [chr(ord('a') + i) for i in range(26) ]
    d = d + [chr(ord('A') + i) for i in range(26) ]
    uid = ""
    tm = int(time.time())
    while tm>0:
        rem = tm % len(d)
        tm//=len(d)
        uid = uid + d[rem]
    
    while len(uid) < length:
        uid = uid + d[randint(0,len(d)-1)]

    return uid

@auth.route('/login')
def loginPage():
    if userLoggedIn():
        return redirect(url_for('client.dashboard'))
    return render_template('login.html')

@auth.route('/signup')
def signupPage():
    if userLoggedIn():
        return redirect(url_for('main.index'))
    return render_template('signup.html')


@auth.route('/companySignup')
def companySignup():
    if userLoggedIn():
        return redirect(url_for('main.index'))
    return render_template('company_signup.html')

@auth.route('/logout')
def logout():
    session.pop('loggedIn', None)
    return redirect(url_for('auth.loginPage'))

@auth.route('/login', methods= ['POST'])
def login():
    if userLoggedIn():
        return redirect(url_for('main.index'))
    if validLogin(request.form['email'], request.form['password']):
        loginUser(request.form['email'])
        return openDashboard()
    flash('Invalid Login Credentials')
    return redirect(url_for('auth.loginPage'))

@auth.route('/signup', methods= ['POST'])
def signup():
    if userLoggedIn():
        return redirect(url_for('main.index'))
    if validateSignupRequest(request.form):
        addUser(request.form, tp="client")
        loginUser(request.form['email'])
        return openDashboard()
    return redirect(url_for('auth.signupPage'))        


@auth.route('/company_signup', methods= ['POST'])
def company_signup():
    if userLoggedIn():
        return redirect(url_for('main.index'))
    if validateCompanySignupRequest(request.form):
        addUser(request.form, tp="company")
        loginUser(request.form['email'])
        return openDashboard() 
    return redirect(url_for('auth.company_signup_Page'))


def openDashboard():
    if userType('client'):
        return redirect(url_for('client.dashboard'))
    if userType('shareholder'):
        return redirect(url_for('shareholders.dashboard'))
    if userType('agent'):
        return redirect(url_for('agent.dashboard'))
    if userType('employee'):
        return redirect(url_for('staff.dashboard'))
    if userType('company'):
        return redirect(url_for('organizations.dashboard'))
    if userType('admin'):
        return redirect(url_for('admin.dashboard'))

def addClient(requestForm):
    dbCursor = db.cursor()
    agentID = getAgentID()
    sql = "INSERT INTO clients (client_PAN,client_DOB,client_name,client_ph,branch_ID,agent_ID,client_email,client_sex,client_ID,company_reg_no,client_aadhar) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s)"
    val = (requestForm['pan'], requestForm['dob'], 
    requestForm['name'], requestForm['phone'],
    requestForm['branch'], getAgentID(),
    requestForm['email'], getGender(requestForm['sex']),
    generateUID(12),requestForm['aadhar'])
    dbCursor.execute(sql, val)
    db.commit()
    dbCursor.close()

def getAgentID():
    dbCursor = db.cursor(buffered=True)
    sql = "SELECT agent_ID, COUNT(agent_ID) FROM clients GROUP BY agent_ID ORDER BY COUNT(agent_ID) ASC"
    dbCursor.execute(sql)
    agentID = dbCursor.fetchall()[0][0]
    dbCursor.close()
    return agentID

def getAge(dob):
    dob = datetime.strptime(dob, "%Y-%m-%d").date()
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def getGender(gender):
    return "M" if gender=="male" else "F"

def userLoggedIn():
    return ('loggedIn' in session)

def userType(userType):
    return (session['userType'] == userType)

def loginUser(email):
    session['loggedIn'] = True
    session['email'] = email
    session['id'], session['username'], session['userType'] = getUserInfo(email)

def getUserInfo(email):
    dbCursor = db.cursor()
    sql = "SELECT user_type, username FROM login WHERE email = %s"
    val = (email, )
    dbCursor.execute(sql,val)
    res = dbCursor.fetchone()
    usertype = res[0]
    username = res[1]
    userID = 0
    if usertype == 'client':
        sql = "SELECT client_ID FROM clients WHERE client_email = %s"
        val = (email,)
        dbCursor.execute(sql,val)
        userID = dbCursor.fetchone()[0]
    elif usertype == 'employee':
        sql = "SELECT employee_ID FROM staff WHERE employee_email = %s"
        val = (email,)
        dbCursor.execute(sql,val)
        userID = dbCursor.fetchone()[0]
    elif usertype == 'agent':
        sql = "SELECT agent_ID FROM agents WHERE agent_email = %s"
        val = (email,)
        dbCursor.execute(sql,val)
        userID = dbCursor.fetchone()[0]
    elif usertype == 'shareholder':
        sql = "SELECT share_ID FROM shareholders WHERE share_email = %s"
        val = (email,)
        dbCursor.execute(sql,val)
        userID = dbCursor.fetchone()[0]
    elif usertype == 'company':
        sql = "SELECT company_ID FROM companies WHERE company_email = %s"
        val = (email,)
        dbCursor.execute(sql,val)
        userID = dbCursor.fetchone()[0]

    dbCursor.close()
    return userID, username, usertype


def addUser(requestForm, tp=""):
    dbCursor = db.cursor()
    sql = "INSERT INTO login (username, password, email, user_type) VALUES (%s, %s, %s, %s) "
    val = (requestForm['username'], requestForm['password'], requestForm['email'], tp)
    dbCursor.execute(sql, val)
    db.commit()
    dbCursor.close()
    if tp=='client':
        addClient(requestForm)
    if tp=='company':
        addCompany(requestForm)

def validLogin(email, password):
    dbCursor = db.cursor()
    sql = "SELECT * FROM login WHERE email = %s AND password = %s"
    val = (email, password)
    dbCursor.execute(sql, val)
    res = True if dbCursor.fetchone() else False
    dbCursor.close()
    return res


def validateSignupRequest(formData):
    return (checkNotPresent('username',formData['username'], 'login', 'Username already in use') 
        and checkNotPresent('email',formData['email'], 'login', 'Email already in use')
        and checkNotPresent('client_ph',formData['phone'], 'clients', 'Phone already in use')
        and checkNotPresent('client_aadhar',formData['aadhar'], 'clients', 'Aadhar already linked to another account')
        and checkNotPresent('client_PAN',formData['pan'], 'clients', 'PAN number already linked to another account')
    ) 

############

#COMPANY SIGNUP
def validateCompanySignupRequest(formData):
    return ( checkNotPresent('username',formData['username'], 'login', 'Username already in use')
        and checkNotPresent('email',formData['email'], 'login', 'Email already in use')
        and checkNotPresent('company_ph',formData['phone'], 'companies', 'Phone already in use')
        and checkNotPresent('company_reg_no',formData['regNo'], 'companies', 'Registration no linked to another account')
    )

def addCompany(requestForm):
    dbCursor = db.cursor()
    
    currDate = datetime.today().strftime('%Y-%m-%d')
    offerDesc = None
    discountFactor = None
    if requestForm['offer'] == "1":
        offerDesc = "Flat Discount"
        discountFactor = 0.2
    else:
        offerDesc = "Limited Discount"
        discountFactor = 0.3
    
    company_ID = generateUID(12)

    sql = "INSERT INTO companies (collab_duration,collab_start_date,company_name,company_ID,company_ph,company_email,company_reg_no) \
        VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (requestForm['duration'], currDate, 
    requestForm['name'], company_ID,
    requestForm['phone'],requestForm['email'], 
    requestForm['regNo'])

    dbCursor.execute(sql, val)
    db.commit()
    

    offerID = generateUID(6)
    sql = "INSERT INTO offers (company_ID, offer_desc, discount_factor, offer_ID, active) VALUES (%s, %s, %s, %s, %s)"
    val = (company_ID,offerDesc, discountFactor, offerID, 1)
    dbCursor.execute(sql, val)
    db.commit()



############

def checkNotPresent(attr, val, table, flashMessage=""):
    dbCursor = db.cursor()
    sql = "SELECT * FROM " + table + " WHERE " + attr + " = %s"
    val = (val, )
    dbCursor.execute(sql, val)
    res = False if dbCursor.fetchone() else True
    dbCursor.close()
    if len(flashMessage)>0 and not res:
        flash(flashMessage)
    return res


