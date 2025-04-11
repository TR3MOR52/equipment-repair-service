import jwt
from functools import wraps
from flask import request, redirect, url_for, g, render_template
from prog.utils.security import jwt_secret
from prog.services.access_control import is_action_allowed

def access_required(entity, action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return redirect(url_for('auth.login'))

            try:
                payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
                role = payload.get('role')
                g.user_id = payload.get('employee_id')
                g.user_role = role
            except jwt.ExpiredSignatureError:
                return redirect(url_for('auth.login'))
            except jwt.InvalidTokenError:
                return redirect(url_for('auth.login'))

            if not is_action_allowed(role, entity, action):
                return render_template('errors/403.html')

            return f(*args, **kwargs)
        return wrapper
    return decorator

def access_required_dynamic(action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return redirect(url_for('auth.login'))

            try:
                payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
                role = payload.get('role')
                g.user_id = payload.get('employee_id')
                g.user_role = role
            except jwt.ExpiredSignatureError:
                return redirect(url_for('auth.login'))
            except jwt.InvalidTokenError:
                return redirect(url_for('auth.login'))

            # Извлекаем table_name из kwargs
            entity = kwargs.get('table_name')
            if not is_action_allowed(role, entity, action):
                return render_template('errors/403.html'), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
