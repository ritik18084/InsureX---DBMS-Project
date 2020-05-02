from flask import Blueprint, session, request, redirect, url_for, render_template
from . import db
from .auth import userLoggedIn, userType, generateUID
from datetime import datetime
organizations = Blueprint('organizations',__name__)


@organizations.route('/orgDashboard')
def dashboard():
    if not(userLoggedIn() and userType('company')):
        return
    return render_template('organization/dashboard.html')

@organizations.route('/orgClients')
def dashboardClients():
    if not(userLoggedIn() and userType('company')):
        return
    return render_template('organization/clientInfo.html')

@organizations.route('/orgCollab')
def dashboardCollab():
    if not(userLoggedIn() and userType('company')):
        return
    return render_template('organization/collab.html')


@organizations.context_processor
def viewOrgProfile():
    if not(userLoggedIn() and userType('company')):
        return
    dbCursor = db.cursor()
    company_ID = session['id']
    sql = "SELECT company_ph, company_name, company_reg_no FROM companies WHERE company_ID = %s "
    val = (company_ID, )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'orgProfile' : [session['username'], res[0], session['email'], res[1], res[2]]}

@organizations.context_processor
def viewOrgNumberClients():
    if not(userLoggedIn() and userType('company')):
        return
    dbCursor = db.cursor()
    sql = "SELECT COUNT(*) FROM clients A, companies B WHERE A.company_reg_no = B.company_reg_no AND B.company_ID = %s "
    val = (session['id'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'orgClientCount' : res}

@organizations.context_processor
def viewOrgClients():
    if not(userLoggedIn() and userType('company')):
        return
    dbCursor = db.cursor()
    sql = "SELECT A.client_name, A.client_ph, A.client_email FROM clients A, companies B WHERE A.company_reg_no = B.company_reg_no AND B.company_ID = %s "
    val = (session['id'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'orgClients' : res}


   
@organizations.context_processor
def viewCollabDetails():
    if not(userLoggedIn() and userType('company')):
        return
    
    dbCursor = db.cursor()
    
    sql = "SELECT A.offer_desc, B.collab_start_date, B.collab_duration FROM offers A, companies B WHERE B.company_ID = %s AND A.company_ID = B.company_ID AND A.active = 1"
    val = (session['id'], )
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()

    if res:
        return {'collabExists' : True, 'collabDetails' : res}
    else:
        return {'collabExists' : False}


@organizations.route('/extendCollabDuration', methods= ['POST'])
def extendCollabDuration():
    if not(userLoggedIn() and userType('company')):
        return
    dbCursor = db.cursor()
    sql = "UPDATE companies SET collab_duration = collab_duration + " + str(int(request.form['extension'])) + " WHERE company_ID = %s "
    val = (session['id'],)
    dbCursor.execute(sql, val)
    db.commit()
    dbCursor.close()
    return redirect(url_for('organizations.dashboardCollab'))


@organizations.route('/applyCollab', methods= ['POST'])
def applyCollab():
    if not(userLoggedIn() and userType('company')):
        return
    
    if viewCollabDetails()['collabExists']:
        return
    
    dbCursor = db.cursor()
    
    currDate = datetime.today().strftime('%Y-%m-%d')
    offerDesc = None
    discountFactor = None
    if request.form['offer'] == "1":
        offerDesc = "Flat Discount"
        discountFactor = 0.2
    else:
        offerDesc = "Limited Discount"
        discountFactor = 0.3
 
    sql = "UPDATE companies SET collab_start_date = %s, collab_duration = %d WHERE company_ID = %s"
    val = (currDate, request.form['duration'])
    dbCursor.execute(sql, val)
    db.commit()
    
    offerID = generateUID(6)
    sql = "INSERT INTO offers (company_ID, offer_desc, discount_factor, offer_ID, active) VALUES (%s, %s, %f, %s, %d)"
    val = (session['id'],offerDesc, discountFactor, offerID, 1)
    dbCursor.execute(sql, val)
    db.commit()

    dbCursor.close()
    return redirect(url_for('organizations.dashboardCollab'))
