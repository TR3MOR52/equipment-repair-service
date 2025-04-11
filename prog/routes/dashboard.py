from flask import Blueprint, render_template, request, redirect, url_for, g, abort
from prog.utils.decorators import access_required, access_required_dynamic
from prog.utils.security import jwt_secret, login_required
from prog.services.access_control import ACCESS_MATRIX, is_action_allowed
from prog.utils.db import get_db_connection
import jwt
from psycopg2.extras import RealDictCursor


# 
# 
#  TODO: ДОДЕЛАТЬ USER_LOGIN (чтобы вставлялся в audit_log)
# 
# 




dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth.login'))

    try:
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        role = payload.get('role')
        login = payload.get('login')
        g.user_role = role
        g.user_login = login
    except jwt.ExpiredSignatureError:
        return redirect(url_for('auth.login'))
    except jwt.InvalidTokenError:
        return redirect(url_for('auth.login'))

    role_permissions = ACCESS_MATRIX.get(role, {})
    readable_tables = [table for table, actions in role_permissions.items() if 'R' in actions]

    return render_template('index.html', role=role, tables=readable_tables)

@dashboard_bp.route('/view/<table_name>')
@login_required
@access_required_dynamic('R')
def view_table(table_name):
    role = g.user_role
    if not is_action_allowed(role, table_name, 'R'):
        abort(403)

    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(f'SELECT * FROM {table_name} LIMIT 50')
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
        except Exception as e:
            conn.close()
            return f"Ошибка при получении данных из {table_name}: {e}", 500
    conn.close()

    id_col = f"{table_name}_id"
    return render_template('table_list.html', table=table_name, columns=colnames, rows=rows, id_col=id_col)

# @dashboard_bp.route('/<table_name>/create', methods=['GET', 'POST'])
# @login_required
# @access_required_dynamic('C')
# def create_record(table_name):
#     conn = get_db_connection()
#     with conn.cursor(cursor_factory=RealDictCursor) as cur:
#         cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
#         columns = [row[0] for row in cur.fetchall() if row[0] != 'employee_id']
#     if request.method == 'POST':
#         values = [request.form[col] for col in columns]
#         placeholders = ', '.join(['%s'] * len(values))
#         col_list = ', '.join(columns)
#         with conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 cur.execute(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})", values)
#         return redirect(url_for('dashboard.view_table', table_name=table_name))
#     return render_template('table_create.html', table=table_name, columns=columns)

@dashboard_bp.route('/<table_name>/create', methods=['GET', 'POST'])
@login_required
@access_required_dynamic('C')
def create_record(table_name):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,)
        )
        columns = [row['column_name'] for row in cur.fetchall() if row['column_name'] != f'{table_name}_id']  # исключаем PK

    if request.method == 'POST':
        values = [request.form[col] for col in columns]
        placeholders = ', '.join(['%s'] * len(values))
        col_list = ', '.join(columns)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SET LOCAL "app.current_role" = %s', (g.user_role,))
                cur.execute('SET LOCAL "app.current_login" = %s', (g.user_login,))
                cur.execute(
                    f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})", values
                )
        return redirect(url_for('dashboard.view_table', table_name=table_name))

    return render_template('table_create.html', table=table_name, columns=columns)


@dashboard_bp.route('/<table_name>/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@access_required_dynamic('U')
def edit_record(table_name, record_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(f"SELECT * FROM {table_name} WHERE {table_name}_id = %s", (record_id,))
    record = cur.fetchone()
    colnames = [desc[0] for desc in cur.description]

    if request.method == 'POST':
        updates = [f"{col} = %s" for col in colnames if col != f"{table_name}_id"]
        values = [request.form[col] for col in colnames if col != f"{table_name}_id"]
        values.append(record_id)
        cur.execute('SET LOCAL "app.current_role" = %s', (g.user_role,))
        cur.execute('SET LOCAL "app.current_login" = %s', (g.user_login,))
        cur.execute(
            f"UPDATE {table_name} SET {', '.join(updates)} WHERE {table_name}_id = %s", values
        )
        conn.commit()
        return redirect(url_for('dashboard.view_table', table_name=table_name))

    conn.close()
    return render_template('table_edit.html', table=table_name, columns=colnames, record=record)

@dashboard_bp.route('/<table_name>/delete/<int:record_id>', methods=['POST'])
@login_required
@access_required_dynamic('D')
def delete_record(table_name, record_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SET LOCAL "app.current_role" = %s', (g.user_role,))
        cur.execute('SET LOCAL "app.current_login" = %s', (g.user_login,))
        cur.execute(f"DELETE FROM {table_name} WHERE {table_name}_id = %s", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard.view_table', table_name=table_name))
