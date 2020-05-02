from flask import Blueprint, session, request, redirect, url_for, render_template, flash
from . import db
from .auth import userLoggedIn, userType, generateUID
from datetime import datetime
from werkzeug.utils import secure_filename
import os

client = Blueprint('client',__name__)

@client.route('/clientDashboard')
def dashboard():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/dashboard.html')

@client.route('/clientInsurances')
def dashboardInsurances():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/insurance.html')

@client.route('/clientViewPolicies')
def dashboardViewPolicies():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/policies.html')

@client.route('/buyInsurance')
def dashboardBuy():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/buy.html')

@client.route('/payDues')
def dashboardPayDues():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/pay.html')

@client.route('/transactionHistory')
def dashboardHistory():
    if not(userLoggedIn() and userType('client')):
        return
    return render_template('client/history.html')


@client.context_processor
def viewprofile():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT A.client_ph,A.client_name, A.client_aadhar, A.client_PAN,A.client_DOB, A.client_sex \
        ,B.agent_name, B.agent_ph, B.agent_email, C.branch_name, A.client_ID FROM clients A, agents B, branch C WHERE A.client_ID=%s AND A.agent_ID = B.agent_ID AND A.branch_ID = C.branch_ID" 
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    ret = [session['username'], res[0], session['email']] + list(res)[1:]
    return {'clientInfo' : ret }


@client.context_processor
def viewBuyPolicies():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT ins_type,policy_name,policy_key, coverage_amt, premium, duration, eligibility_cond,\
    terms_conditions FROM policies"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'buyPolicies' : res}

@client.context_processor
def viewallpolicies():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT policy_name, ins_type, coverage_amt, premium,eligibility_cond,\
    terms_conditions FROM policies"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'allPolicies' : res}

@client.context_processor
def viewallTransactions():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT A.payment_datetime, A.amount, B.Unique_Ins_ID, C.ins_type, C.policy_name \
    FROM transactions A, insurances B, policies C \
    WHERE A.Unique_Ins_ID = B.Unique_Ins_ID AND B.client_ID = %s AND C.policy_key = B.policy_key \
    ORDER BY A.payment_datetime DESC"
    val = (session['id'], )
    dbCursor.execute(sql,val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'allTransactions' : res}


@client.context_processor
def totalInsurances():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT COUNT(*) FROM insurances WHERE client_ID = %s";
    val = (session['id'], )
    dbCursor.execute(sql,val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'totalInsurances' : res}

@client.context_processor
def viewinsurances():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT B.policy_name, B.ins_type, B.coverage_amt, B.premium, A.start_date, B.duration, A.dues \
        FROM insurances A, policies B WHERE A.client_ID = %s AND A.policy_key = B.policy_key"
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'allInsurances' : res}

@client.context_processor
def offers():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()    
    sql = "SELECT A.discount_factor FROM offers A, companies B, clients C \
        WHERE A.company_ID = B.company_ID AND A.active = 1 AND B.company_reg_no = C.company_reg_no AND C.client_ID = %s"
    val = (session['id'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    if res:
        return {'offerValid' : True, 'offerDiscount' : res[0]}
    else:
        return {'offerValid' : False}


@client.context_processor
def getDues():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    sql = "SELECT B.policy_name, B.coverage_amt ,B.premium, A.dues, A.Unique_ins_ID \
        FROM insurances A, policies B WHERE A.client_ID = %s AND A.policy_key = B.policy_key AND A.dues > 0"
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'dues' : res}

@client.route("/paydue", methods =['POST'])
def paydue():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    currDateTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    sql = "SELECT dues FROM insurances WHERE Unique_Ins_ID = %s"
    val = (request.form['id'],)
    dbCursor.execute(sql,val)
    res = dbCursor.fetchone()
    if res:
        amount = res[0]
        sql = "INSERT INTO transactions (transaction_ID, Unique_ins_ID, amount, payment_datetime) VALUES (%s, %s, %s, %s)" 
        val = (generateUID(16),request.form['id'],amount,currDateTime)
        dbCursor.execute(sql, val)
        db.commit()
        sql = "UPDATE insurances SET dues=0 WHERE Unique_Ins_ID = %s"
        val = (request.form['id'], )
        dbCursor.execute(sql,val)
        db.commit()
        dbCursor.close()
        flash('Transaction Successful')
        return redirect(url_for('client.dashboardPayDues'))


@client.route('/buyInsurance', methods=['POST'])
def boughtInsurance():
    if not(userLoggedIn() and userType('client')):
        return
    dbCursor = db.cursor()
    policy_key = request.form['policy_key']
    sql = "SELECT ins_type FROM policies WHERE policy_key=%s"
    val = (policy_key,)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    if not res:
        return
    insType = res[0]
    if insType == "Home":
        return buyHome(request)
    elif insType == "Vehicle":
        return buyVehicle(request)
    elif insType == "Medical":
        return buyMedical(request)
    elif insType == "Travel":
        return buyTravel(request)
    else:
        return buyLife(request)


def buyHome(req):
    if 'file' not in req.files:
        flash('No file Provided')
        return redirect(url_for('client.dashboardBuy'))
    file = req.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('client.dashboardBuy'))
    if file:

        dbCursor = db.cursor()
    
        unique_ins_id = generateUID(12)
        path = unique_ins_id
        currDate = datetime.today().strftime('%Y-%m-%d')
        
        sql = "SELECT branch_ID from clients where client_ID = %s"
        val = (session['id'], )
        dbCursor.execute(sql, val)
        branchID = dbCursor.fetchone()[0]

        dbCursor.close()

        dbCursor = db.cursor()

        sql = "INSERT INTO insurances (policy_key, client_ID, start_date, branch_ID, Unique_Ins_ID, dues) values (%s, %s, %s, %s, %s, 0)"
        val = (req.form['policy_key'], session['id'], currDate, branchID, unique_ins_id)
        dbCursor.execute(sql,val)
        db.commit()

        dbCursor.close()
        
        dbCursor = db.cursor()

        filename = secure_filename(file.filename)
        file.save(path)
        sql = "INSERT INTO home_insurance (Unique_Ins_ID,path_to_prop_papers,prop_location,owners_names,prop_area) VALUES (%s, %s, %s, %s, %s)" 
        val =  (unique_ins_id, path, req.form['location'],req.form['ownerName'],int(req.form['area']))
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()
        flash('Purchase Successfull')
        return redirect(url_for('client.dashboardBuy'))

    flash('No selected file')
    return redirect(url_for('client.dashboardBuy'))
    

def buyVehicle(req):
    dbCursor = db.cursor()
    
    
    sql = "SELECT * FROM vehicle_insurance WHERE RC_num = %s" 
    val = (req.form['rcno'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    
    if res:
        flash('RC already linked to another insurance')
        return redirect(url_for('client.dashboardBuy')) 
    
    
    
    if 'file' not in req.files:
        flash('No file Provided')
        return redirect(url_for('client.dashboardBuy'))
    file = req.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('client.dashboardBuy'))
    
    if file:
        unique_ins_id = generateUID(12)
        path = unique_ins_id
        currDate = datetime.today().strftime('%Y-%m-%d')

        sql = "SELECT branch_ID from clients where client_ID = %s"
        val = (session['id'], )
        dbCursor.execute(sql, val)
        branchID = dbCursor.fetchone()[0]

        sql = "INSERT INTO insurances (policy_key, client_ID, start_date, branch_ID, Unique_Ins_ID, dues) values (%s, %s, %s, %s, %s, %s)"
        val = (req.form['policy_key'], session['id'], currDate, branchID, unique_ins_id, 0)
        dbCursor.execute(sql,val)
        db.commit()


        filename = secure_filename(file.filename)
        file.save(path)
        sql = "INSERT INTO vehicle_insurance (Unique_Ins_ID, vehicle_ID, vehicle_type, RC_num, Path_to_RC)" \
            "VALUES (%s, %s, %s, %s, %s)" 
        val = (unique_ins_id, req.form['vehicleID'], req.form['type'],req.form['rcno'],path)
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()
        flash('Purchase Successfull')
        return redirect(url_for('client.dashboardBuy'))

    flash('No selected file')
    return redirect(url_for('client.dashboardBuy'))

def buyTravel(req):
    dbCursor = db.cursor()
    
    unique_ins_id = generateUID(12)
    path = unique_ins_id
    currDate = datetime.today().strftime('%Y-%m-%d')
    
    sql = "SELECT branch_ID from clients where client_ID = %s"
    val = (session['id'], )
    dbCursor.execute(sql, val)
    branchID = dbCursor.fetchone()[0]

    sql = "INSERT INTO insurances (policy_key, client_ID, start_date, branch_ID, Unique_Ins_ID, dues) values (%s, %s, %s, %s, %s, %s)"
    val = (req.form['policy_key'], session['id'], currDate, branchID, unique_ins_id, 0)
    dbCursor.execute(sql,val)
    db.commit()

    sql = "INSERT INTO travel_insurance (travel_type,travel_details,Unique_Ins_ID,travel_date) VALUES (%s, %s, %s, %s)" 
    val = (req.form['travelType'], req.form['details'], unique_ins_id, req.form['date'])
    
    dbCursor.execute(sql,val)
    db.commit()
    dbCursor.close()
    
    flash('Purchase Successfull')
    return redirect(url_for('client.dashboardBuy'))

def buyLife(req):
    dbCursor = db.cursor()
     
    if 'file' not in req.files:
        flash('No file Provided')
        return redirect(url_for('client.dashboardBuy'))
    file = req.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('client.dashboardBuy'))
    
    if file:

        dbCursor = db.cursor()
    
        unique_ins_id = generateUID(12)
        path = unique_ins_id
        currDate = datetime.today().strftime('%Y-%m-%d')
        
        sql = "SELECT branch_ID from clients where client_ID = %s"
        val = (session['id'], )
        dbCursor.execute(sql, val)
        branchID = dbCursor.fetchone()[0]

        sql = "INSERT INTO insurances (policy_key, client_ID, start_date, branch_ID, Unique_Ins_ID, dues) values (%s, %s, %s, %s, %s, %s)"
        val = (req.form['policy_key'], session['id'], currDate, branchID, unique_ins_id, 0)
        dbCursor.execute(sql,val)
        db.commit()

        filename = secure_filename(file.filename)
        file.save(path)
        
        sql = "INSERT INTO life_insurance (nominee_name2,nominee_name1,path_to_birth_certificate,Unique_Ins_ID) VALUES (%s, %s, %s, %s)" 
        val = (req.form['nom1name'], req.form['nom2name'],path, unique_ins_id,)
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()
        
        flash('Purchase Successfull')
        return redirect(url_for('client.dashboardBuy'))

    flash('No selected file')
    return redirect(url_for('client.dashboardBuy'))

def buyMedical(req):
     
    if 'file' not in req.files:
        flash('No file Provided')
        return redirect(url_for('client.dashboardBuy'))
    file = req.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('client.dashboardBuy'))
    
    if file:

        dbCursor = db.cursor()
    
        unique_ins_id = generateUID(12)
        path = unique_ins_id
        currDate = datetime.today().strftime('%Y-%m-%d')
        
        sql = "SELECT branch_ID from clients where client_ID = %s"
        val = (session['id'], )
        dbCursor.execute(sql, val)
        branchID = dbCursor.fetchone()[0]

        sql = "INSERT INTO insurances (policy_key, client_ID, start_date, branch_ID, Unique_Ins_ID, dues) values (%s, %s, %s, %s, %s, %s)"
        val = (req.form['policy_key'], session['id'], currDate, branchID, unique_ins_id, 0)
        dbCursor.execute(sql,val)
        db.commit()

        filename = secure_filename(file.filename)
        file.save(path)
        sql = "INSERT INTO medical_insurance (Unique_Ins_ID,path_to_medical_bills,medical_history) VALUES (%s, %s, %s)" 
        val =  (unique_ins_id, path, req.form['history'])
        dbCursor.execute(sql, val)
        db.commit()
        dbCursor.close()

        flash('Purchase Successfull')
        return redirect(url_for('client.dashboardBuy'))

    flash('No selected file')
    return redirect(url_for('client.dashboardBuy'))

