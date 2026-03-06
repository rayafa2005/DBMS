from flask import Blueprint, render_template, session, redirect, url_for, request
from db import get_db

index_bp = Blueprint('index', __name__, url_prefix='/index')

@index_bp.route('/')
def index():
    print("index page accessed")
    if 'user_id' not in session:
        print("user is not logged in")
        return redirect(url_for('login_page'))
    print('user is logged in')
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', products=products)

@index_bp.route('/filter')
def filter_products():
    price = request.args.get('price')
    category = request.args.get('category')
    condition = request.args.get('condition')

    query = "SELECT p.* FROM products p LEFT JOIN categories c ON p.category_id = c.category_id WHERE 1=1"
    params = []

    if price:
        if price == '100-500':
            query += " AND p.price BETWEEN %s AND %s"
            params.extend([100, 500])
        elif price == '500-1000':
            query += " AND p.price BETWEEN %s AND %s"
            params.extend([500, 1000])

    if category:
        query += " AND c.name = %s"
        params.append(category)

    if condition:
        query += " AND p.conditions = %s"
        params.append(condition)

    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('partials/products.html', products=products)

@index_bp.route('/view_prd/<int:product_id>')
def view_product(product_id):
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('view_prd.html', product=product)
