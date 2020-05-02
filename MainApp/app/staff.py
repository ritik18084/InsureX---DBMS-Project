from flask import Blueprint, session, request, redirect, url_for, render_template
from . import db
from .auth import userLoggedIn, userType

staff = Blueprint('staff',__name__)



@staff.route('/staffDashboard')
def dashboard():
    if not(userLoggedIn() and userType('employee')):
        return
    return render_template('staff/dashboard.html')


@staff.route('/staffClientInfo')
def dashboardClient():
    if not(userLoggedIn() and userType('employee')):
        return
    return render_template('staff/clientInfo.html')

@staff.route('/staffInsuranceInfo')
def dashboardInsurance():
    if not(userLoggedIn() and userType('employee')):
        return
    return render_template('staff/insurance.html', staffClientQuery=False)


@staff.context_processor
def viewStaffProfile():
	if not(userLoggedIn() and userType('employee')):
		return
	dbCursor = db.cursor()
	sql = "SELECT A.employee_name, \
	A.employee_aadhar, A.employee_PAN, B.branch_name,A.department, A.position, A.salary, A.employee_ph \
	FROM staff A, branch B  \
	WHERE employee_ID = %s AND A.branch_ID=B.branch_ID"
	employee_ID = session['id']
	val = (employee_ID,)
	dbCursor.execute(sql, val)
	res = dbCursor.fetchone()
	dbCursor.close()
	return {'staffProfile' : [session['username'], res[7], session['email'], res[0], res[1], res[2],res[3], res[4],res[5],res[6]]}

@staff.route('/viewClientDetails', methods = ["POST"])
def viewClientDetails():
	if not(userLoggedIn() and userType("employee")):
		return
	dbCursor = db.cursor()
	sql = "SELECT client_name,client_ph,client_email,branch_ID,client_aadhar,client_PAN, "\
	"client_DOB,client_sex,agent_name,agent_ph,agent_email  FROM clients c, agents a WHERE "\
	"c.client_ID = %s AND c.agent_ID=a.agent_ID"
	val = (request.form['clientID'],)
	dbCursor.execute(sql, val)
	res = dbCursor.fetchone()
	sql = "SELECT Unique_Ins_ID, ins_type, DATE_ADD(start_date, INTERVAL duration YEAR) as end_date  FROM \
	insurances, policies WHERE policies.policy_key=insurances.policy_key AND client_ID = %s"
	val = (request.form['clientID'],)
	dbCursor.execute(sql, val)
	res2 = dbCursor.fetchall()
	dbCursor.close()
	if res:
		return render_template('staff/clientInfo.html',staffClientQuery=True, clientInfo=res, staffClientIns=res2)
	else:
		return render_template('staff/clientInfo.html',staffClientQuery=False)

@staff.route("/viewStaffInsurance", methods = ['POST'])
def viewInsurance():
	if not(userLoggedIn() and userType('employee')):
		return
	dbCursor = db.cursor()
	sql = "SELECT c.client_name, c.client_ID,c.agent_ID,ins_type, " \
	"policy_name,coverage_amt, ppm, start_date,  DATE_ADD(start_date, INTERVAL duration YEAR), "\
	"dues, Unique_Ins_id FROM clients c, insurances i, policies p WHERE "\
	"i.Unique_Ins_id = %s AND c.client_ID=i.client_ID AND p.policy_key=i.policy_key"
	val = (request.form['insID'],)
	dbCursor.execute(sql, val)
	res = dbCursor.fetchone()
	dbCursor.close()
	if res:
		return render_template('staff/insurance.html',staffInsQuery=True, insInfo=res)
	else:
		return render_template('staff/insurance.html',staffInsQuery=False)
	
	