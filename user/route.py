from flask import jsonify, request
from app import app
from user.models import User

# API Routes (POST requests)
@app.route('/login', methods=['POST'])
def login_submit():
    return User().login()

@app.route('/signup', methods=['POST'])
def signup_submit():
    return User().signUp()