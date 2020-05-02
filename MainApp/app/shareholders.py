from flask import Blueprint, session, request, redirect, url_for, render_template
from . import db, app
from .auth import userLoggedIn,userType
from datetime import datetime

shareholders = Blueprint('shareholders',__name__)


@shareholders.route('/shareDashboard')
def dashboard():
    if not(userLoggedIn() and userType('shareholder')):
        return
    return render_template('shareholders/dashboard.html')

@shareholders.route('/shareProfit')
def dashboardProfit():
    if not(userLoggedIn() and userType('shareholder')):
        return
    return render_template('shareholders/profit.html')

@shareholders.route('/shareStats')
def dashboardStats():
    if not(userLoggedIn() and userType('shareholder')):
        return
    return render_template('shareholders/stats.html')

@shareholders.route('/shareBranch')
def dashboardBranch():
    if not(userLoggedIn() and userType('shareholder')):
        return
    return render_template('shareholders/branch.html')   


@shareholders.app_context_processor
def activeInsuranceCounts():
    dbCursor = db.cursor()
    currDate = datetime.today().strftime('%Y-%m-%d')
    sql = "SELECT COUNT(*) AS count FROM insurances A, policies B WHERE A.policy_key=B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) > %s"
    val = (currDate, )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'activeInsurances' : res}


@shareholders.app_context_processor
def howManyactiveXYZ():
    dbCursor = db.cursor()
    currDate = datetime.today().strftime('%Y-%m-%d')
    sql = "SELECT B.ins_type, COUNT(*) AS count FROM insurances A, policies B \
        WHERE A.policy_key=B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) > %s \
        GROUP BY B.ins_type"
    val = (currDate, )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'activeXYZ' : res}



@shareholders.app_context_processor
def totalInsuranceCounts():
    dbCursor = db.cursor()
    currDate = datetime.today().strftime('%Y-%m-%d')
    sql = "SELECT COUNT(*) AS count FROM insurances"
    dbCursor.execute(sql)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'totalInsurances' : res}


@shareholders.app_context_processor
def howManytotalXYZ():
    dbCursor = db.cursor()
    currDate = datetime.today().strftime('%Y-%m-%d')
    sql = "SELECT B.ins_type, COUNT(*) AS count FROM insurances A, policies B WHERE A.policy_key = B.policy_key GROUP BY ins_type"
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'totalXYZ' : res}



@shareholders.app_context_processor
def getAnnualProfit():
    years = [2015,2016,2017,2018,2019]
    res = []
    for year in years:
        res.append((year,int(annualProfit(year)[0])))
    return {'annualProfit' : res}

def annualProfit(year):
    dbCursor = db.cursor()
    startDate = '%d-01-01' %(year)
    endDate = '%d-12-31' %(year)
    sql = "SELECT SUM(A.P) as profit FROM " \
        "(SELECT SUM(-1*B.coverage_amt) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) <= %s AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) >= %s UNION ALL " \
        "SELECT SUM(TIMESTAMPDIFF(MONTH, %s, DATE_ADD(A.start_date, INTERVAL B.duration YEAR))*B.ppm) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) <= %s AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) >= %s UNION ALL " \
        "SELECT SUM(12*B.ppm) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND A.start_date <= %s AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) >= %s UNION ALL " \
        "SELECT SUM(TIMESTAMPDIFF(MONTH, A.start_date, %s)*B.ppm) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND  A.start_date >= %s AND A.start_date <= %s AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) >= %s UNION ALL " \
        "SELECT 0 as P FROM insurances ) AS A " 
    val = (endDate, startDate, startDate, endDate, startDate, startDate, endDate, endDate, startDate, endDate, endDate)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return res

@shareholders.app_context_processor
def netProfit():
    dbCursor = db.cursor()
    currDate = datetime.today().strftime('%Y-%m-%d')
    sql = "SELECT SUM(A.P) as profit FROM " \
        "(SELECT SUM(B.premium-B.coverage_amt) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) <= %s UNION ALL " \
        "SELECT SUM(TIMESTAMPDIFF(MONTH, A.start_date, %s)*B.ppm) as P FROM insurances A, policies B WHERE A.policy_key = B.policy_key AND DATE_ADD(A.start_date, INTERVAL B.duration YEAR) > %s) AS A" 
    val = (currDate, currDate, currDate)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'netProfit' : (int(res[0]),)}

@shareholders.context_processor
def shareUserProfile():
    dbCursor = db.cursor()
    sql = "SELECT equity_percentage, share_name FROM shareholders WHERE share_ID = %s"
    val = (session['id'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'shareUserProfile' : [session['username'], session['email'], res[1], res[0]]}

