from functools import wraps
from flask import request, redirect, url_for, g, render_template
import jwt

jwt_secret = 'your_jwt_secret_key'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('auth.login'))

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            g.user_id = payload['employee_id']
            g.user_role = payload['role']
            g.user_login = payload['login']
        except jwt.ExpiredSignatureError:
            return redirect(url_for('auth.login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                # Убедимся, что пользователь прошёл login_required
                return redirect(url_for('auth.login'))

            if g.user_role not in allowed_roles:
                return render_template('errors/403.html')

            return f(*args, **kwargs)
        return decorated_function
    return decorator

