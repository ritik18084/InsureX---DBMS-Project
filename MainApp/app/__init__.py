from flask import Flask
from os import urandom
import mysql.connector
from datetime import date
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="InsureX"
)

app = None

def updateDues():
  currDate = date.today()
  if currDate > app.config['currDate']:
    dbCursor = db.cursor()
    sql = "UPDATE (insurances A INNER JOIN policies B ON A.policy_key = B.policy_key) \
      INNER JOIN clients C on A.client_ID = C.client_ID \
      SET A.dues=A.dues+B.ppm WHERE TIMESTAMPDIFF(MONTH, A.start_date, curdate()) > \
      TIMESTAMPDIFF(MONTH, A.start_date, DATE_SUB(curdate(), INTERVAL 1 DAY)) AND \
      DATE_ADD(start_date, INTERVAL B.duration YEAR) >= curdate() AND C.company_reg_no IS NULL;"
    dbCursor.execute(sql)
    db.commit()
    sql = "UPDATE (((insurances A INNER JOIN policies B ON A.policy_key = B.policy_key) \
      INNER JOIN clients C on A.client_ID = C.client_ID) \
      INNER JOIN companies D ON D.company_reg_no = C.company_reg_no) \
      INNER JOIN offers E on D.company_ID = E.company_ID \
      SET A.dues=A.dues+(B.ppm*(100-E.discount_factor)/100) \
      WHERE TIMESTAMPDIFF(MONTH, A.start_date, curdate()) > \
      TIMESTAMPDIFF(MONTH, A.start_date, DATE_SUB(curdate(), INTERVAL 1 DAY)) \
      AND DATE_ADD(start_date, INTERVAL B.duration YEAR) >= curdate() AND E.active=1;"
    dbCursor.execute(sql)
    db.commit()
    dbCursor.close()
  app.config['currDate'] = currDate
    


def create_app():
    global app
    app = Flask(__name__)
    app.secret_key = urandom(24)
    
    from .auth import auth
    from .main import main
    from .client import client
    from .agent import agent
    from .staff import staff
    from .admin import admin
    from .shareholders import shareholders
    from .organizations import organizations
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(client)
    app.register_blueprint(agent)
    app.register_blueprint(staff)
    app.register_blueprint(admin)
    app.register_blueprint(shareholders)
    app.register_blueprint(organizations)
    

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=updateDues, trigger="interval", seconds=5)
    app.config['currDate'] = date.today()
  
    
    scheduler.start()

    return app