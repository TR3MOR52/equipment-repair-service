from flask import Blueprint, request, render_template, redirect, url_for, jsonify, make_response
from prog.services.auth_service import authenticate_user
import jwt
import datetime
from prog.utils.security import jwt_secret

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = authenticate_user(login, password)

        if user:
            payload = {
                'employee_id': user['employee_id'],
                'role': user['role'],
                'login': user['login'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            }
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            response = make_response(redirect(url_for('dashboard.index')))
            response.set_cookie('token', token)
            return response
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('token', '', expires=0)
    return response

