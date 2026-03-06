from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from db import get_db

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist')
def wishlist():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT name FROM users WHERE user_id = %s', (user_id,))
    user_name = cursor.fetchone()['name']

    cursor.execute("""
        SELECT p.id, p.name, p.price, p.image
        FROM wishlist w
        JOIN products p ON w.id = p.id
        WHERE w.user_id = %s
    """, (user_id,))
    wishlist_items = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('wishlist.html', wishlist_items=wishlist_items, user_name=user_name)

@wishlist_bp.route('/remove_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM wishlist WHERE user_id = %s AND id = %s', (user_id, product_id))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})
