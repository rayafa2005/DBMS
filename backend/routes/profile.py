from flask import Blueprint, render_template, session, request, jsonify
from db import get_db

profile_bp = Blueprint('profile_bp', __name__, url_prefix='/profile')

@profile_bp.route('/')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return "Unauthorized", 401

    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('profile.html', user_data=user_data, user_name=user_data['name'])

@profile_bp.route('/update', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    data = request.get_json()
    try:
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE users SET name=%s, email=%s, phone=%s, address=%s WHERE user_id=%s
        """, (data['name'], data['email'], data['phone'], data['address'], user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@profile_bp.route('/change_password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    data = request.get_json()
    current, new, confirm = data['current'], data['newpass'], data['confirm']

    if new != confirm:
        return jsonify({'success': False})

    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT password_hash FROM users WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    if not row or row['password_hash'] != current:
        return jsonify({'success': False})

    cursor.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (new, user_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'success': True})
