from flask import Blueprint, session, request, redirect, url_for, render_template
from . import db
from .auth import userLoggedIn

main = Blueprint('main',__name__)

@main.route('/')
def index():
    if userLoggedIn():
        return render_template('index.html')
    return render_template('index.html')
    
