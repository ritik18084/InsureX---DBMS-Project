from flask import Blueprint, session, request, redirect, url_for, render_template
from . import db
from .auth import userLoggedIn,userType

agent = Blueprint('agent',__name__)


@agent.route('/agentDashboard')
def dashboard():
    if not(userLoggedIn() and userType('agent')):
        return
    return render_template('agent/dashboard.html')

@agent.route('/agentClients')
def dashboardClients():
    if not(userLoggedIn() and userType('agent')):
        return
    return render_template('agent/clientInfo.html')

@agent.route('/agentPolicies')
def dashboardPolicies():
    if not(userLoggedIn() and userType('agent')):
        return
    return render_template('agent/policies.html')


@agent.context_processor
def viewsold():
    if not(userLoggedIn() and userType('agent')):
        return
    dbCursor = db.cursor()
    sql = "SELECT B.client_name, B.client_ph, B.client_email ,C.ins_type, A.start_date, C.duration FROM insurances A, clients B, policies C WHERE C.policy_key = A.policy_key AND B.agent_ID=%s AND A.client_ID=B.client_ID"
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchall()
    dbCursor.close()
    return {'agentPoliciesSold' : res}

@agent.context_processor
def viewCountSold():
    if not(userLoggedIn() and userType('agent')):
        return
    dbCursor = db.cursor()
    sql = "SELECT COUNT(*) FROM insurances I, (SELECT client_ID from clients WHERE agent_ID = %s) A WHERE I.client_ID = A.client_ID"
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()[0]
    dbCursor.close()
    return {'agentCountSold' : res}

@agent.context_processor
def viewagentprofile():
    if not(userLoggedIn() and userType('agent')):
        return
    dbCursor = db.cursor()
    sql = "SELECT agent_name,agent_ph,agent_aadhar,commission_factor FROM agents WHERE agent_ID=%s"
    val = (session['id'],)
    dbCursor.execute(sql, val)
    res = dbCursor.fetchone()
    dbCursor.close()
    return {'agentProfile' : [session['username'], res[1], session['email'], res[0], res[2], res[3]]}

@agent.context_processor
def getClientContact():
    if not(userLoggedIn() and userType('agent')):
        return
    dbCursor = db.cursor()
    sql = "SELECT client_name, client_ph, client_email \
    FROM clients WHERE agent_ID= %s"
    agent_ID = session['id']
    val = (agent_ID,)
    dbCursor.execute(sql, val)
    res= dbCursor.fetchall()
    dbCursor.close()
    return {'agentClientContact' : res}

@agent.context_processor
def getClientCount():
    if not(userLoggedIn() and userType('agent')):
        return
    dbCursor = db.cursor()
    sql = "SELECT COUNT(*) \
    FROM clients WHERE agent_ID= %s"
    agent_ID = session['id']
    val = (agent_ID, )
    dbCursor.execute(sql, val)
    res= dbCursor.fetchone()[0]
    dbCursor.close()
    return {'agentClientCount' : res}