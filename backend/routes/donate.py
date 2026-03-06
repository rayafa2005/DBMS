# routes/donate.py
from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import mysql.connector

donate_bp = Blueprint('donate', __name__)

UPLOAD_FOLDER = os.path.join('frontend', 'static', 'product_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Raziya#2005',
        database='raziyadb',
        use_pure=True
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@donate_bp.route('/donate', methods=['GET'])
def donate_page():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT category_id, name FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('donate.html', categories=categories)

@donate_bp.route('/donate/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file.save(filepath)
            return jsonify({"filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid file format."}), 400

@donate_bp.route('/donate/submit', methods=['POST'])
def submit_donation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    try:
        name = request.form['name']
        og_price = int(request.form['og_price'])
        price = og_price * 0.5
        description = request.form['description']
        category = request.form['category']
        condition = request.form['condition']
        quantity = request.form['quantity']
        image_name = request.form['image_name']

        # Preserve original extension
        ext = image_name.rsplit('.', 1)[-1].lower()
        image_filename = f"{secure_filename(name)}.{ext}"

        old_path = os.path.join(UPLOAD_FOLDER, image_name)
        new_path = os.path.join(UPLOAD_FOLDER, image_filename)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        else:
            return jsonify({"error": "Image file not found"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO products (name, description, price, image, category_id, conditions, og_price, seller_id, quantity, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (
            name, description, price, image_filename,
            category if category != 'other' else None,
            condition, og_price, user_id, quantity
        ))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
