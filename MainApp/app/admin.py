import time
from random import randint
from flask import Blueprint, session, request, redirect, url_for, render_template, flash
from . import db
from .auth import userLoggedIn, userType, addUser, generateUID, checkNotPresent
from datetime import datetime

admin = Blueprint('admin',__name__)

# COMMON TO SHAREHOLDERS
@admin.app_context_processor
def viewBranchDetails():
    # if not(userLoggedIn() and (userType('admin') or userType('shareholders'))):
    #     return
    dbCursor = db.cursor()
    sql = "SELECT branch_name, branch_ph, branch_email, \
    (select (select count(*) from staff s where s.branch_ID=b.branch_ID) from dual) as total_employees\
    , (select (select count(*) from insurances i where i.branch_ID=b.branch_ID) from dual) \
    as policies_sold, branch_ID from branch b;"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'branchDetails' :  res}


@admin.route('/adminDashboard')
def dashboard():
    if not(userLoggedIn() and userType('admin')):
        return
    return render_template('admin/dashboard.html')



@admin.route('/adminBranchEmp')
def dashboardBranchEmp():
    if not(userLoggedIn() and userType('admin')):
        return
    return render_template('admin/branchEmp.html',branchEmpQuery=False)
    

@admin.route('/adminDeactivate')
def dashboardDeactivateAcc():
    if not(userLoggedIn() and userType('admin')):
        return
    return render_template('admin/deactivateAccount.html')


@admin.route('/adminAddAgent')
def dashboardAddAgent():
    if not(userLoggedIn() and userType('admin')):
        return
    return render_template('admin/dashboardAddAg.html')


@admin.route('/adminAddEmp')
def dashboardAddEmp():
    if not(userLoggedIn() and userType('admin')):
        return
    return render_template('admin/dashboardAddEmp.html')
    



@admin.context_processor
def viewLogins():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    sql = "SELECT username, email FROM login"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'allLogins' : res}

@admin.route('/removeLogin', methods=['POST'])
def remLogin():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    email = request.form['ID']
    sql = "DELETE FROM login WHERE email=%s"
    val=(email, )
    dbCursor.execute(sql,val)
    db.commit()
    dbCursor.close()
    return redirect(url_for('admin.dashboardDeactivateAcc'))


def generateUID(length=12):
    uid = str(int(time.time()))
    while len(uid) < length:
        uid = uid + str(randint(0,9))
    return uid

@admin.route('/addStaff', methods= ['POST'])
def addStaff():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    if validateAddStaffRequest(request.form):
        addUser(request.form, "employee")
        sql = "INSERT INTO staff(\
        employee_name,employee_ph,employee_email,employee_aadhar,employee_PAN,\
        employee_ID,branch_ID, department, position, salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = (request.form['name'], request.form['phone'], 
        request.form['email'], request.form['aadhar'],
        request.form['pan'], generateUID(12),
        request.form['branch'], request.form['dept'],
        request.form['pos'], request.form['salary'])
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()
    flash("Successfully Registered!","success")
    return redirect(url_for('admin.dashboardAddEmp'))

@admin.route('/addAgent', methods= ['POST'])
def addAgent():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    if validateAddAgentRequest(request.form):
        addUser(request.form, "agent")
        sql = "INSERT INTO agents(agent_name,\
        agent_ph, agent_email, agent_aadhar, agent_ID, commission_factor) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (request.form['name'], request.form['phone'], 
        request.form['email'], request.form['aadhar'],
        generateUID(12), request.form['commission'])
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()
    flash("Successfully Registered!","success")
    return redirect(url_for('admin.dashboardAddAgent'))

def validateAddAgentRequest(formData):
    return (checkNotPresent('username',formData['username'], 'login', 'Username already in use') 
        and checkNotPresent('email',formData['email'], 'login', 'Email already in use')
        and checkNotPresent('agent_ph',formData['phone'], 'agents', 'Phone already in use')
        and checkNotPresent('agent_aadhar',formData['aadhar'], 'agents', 'Aadhar already linked to another account')
    ) 

def validateAddStaffRequest(formData):
    return (checkNotPresent('username',formData['username'], 'login', 'Username already in use') 
        and checkNotPresent('email',formData['email'], 'login', 'Email already in use')
        and checkNotPresent('employee_ph',formData['phone'], 'staff', 'Phone already in use')
        and checkNotPresent('employee_aadhar',formData['aadhar'], 'staff', 'Aadhar already linked to another account')
        and checkNotPresent('employee_PAN',formData['pan'], 'staff', 'PAN already linked to another account')
    ) 


@admin.context_processor
def checkProfit():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    sql = "SELECT   A.branch_ID,   B.branch_name,   SUM(A.P) AS profit FROM   (SELECT i.branch_ID,\
           SUM(p.premium - p.coverage_amt) AS P     FROM insurances i, policies p WHERE\
                  p.policy_key = i.policy_key AND DATE_ADD(start_date, INTERVAL duration YEAR) <= curdate()\
                 GROUP BY branch_ID UNION ALL SELECT  i.branch_ID, SUM(TIMESTAMPDIFF(MONTH,\
                            i.start_date,curdate()) * p.ppm) AS P FROM \
                            insurances i, policies p     WHERE \
                            DATE_ADD(start_date, INTERVAL duration YEAR) > curdate()     GROUP BY       i.branch_ID     \
                            UNION ALL SELECT branch.branch_ID, 0 AS P FROM branch) AS A   \
                            INNER JOIN \
    branch B ON A.branch_ID = B.branch_ID GROUP BY   B.branch_ID"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    print(res)
    return {'branchProfit' : res}


@admin.route('/viewbranchStaff', methods= ['POST'])
def viewbranchStaff():
    if not(userLoggedIn() and userType('admin')):
        return
    dbCursor = db.cursor()
    branchID = request.values.get('branchID')
    sql = "SELECT employee_name, employee_ph, employee_email,\
    employee_aadhar,employee_PAN,employee_ID, branch_ID, department, position, salary FROM staff WHERE branch_ID = %s "
    val = (branchID, )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    if res:
        return render_template('admin/branchEmp.html', branchEmpQuery=True, branchEmp=res)
    else:
        return render_template('admin/branchEmp.html', branchEmpQuery=False)






