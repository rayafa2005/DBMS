from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
from flask import render_template
from db import get_db

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/cart')

@cart_bp.route('/')
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    cart_id = cart_row['cart_id'] if cart_row else None

    cart_items = []
    total = 0

    if cart_id:
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.og_price,
                   SUBSTRING_INDEX(p.image, '/', -1) AS image,
                   p.quantity AS max_qty, ci.quantity
            FROM cart_items ci
            JOIN products p ON ci.id = p.id
            WHERE ci.cart_id = %s
        ''', (cart_id,))
        cart_items = cursor.fetchall()

        total = sum(item['price'] * item['quantity'] for item in cart_items)

    cursor.close()
    db.close()

    # 👇👇 Add this block instead of return render_template(...)
    from flask import make_response
    response = make_response(render_template('cart.html', cart_items=cart_items, total=total, user_name=session.get('user_name')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_item(product_id):
    user_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()

    # Get cart_id
    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    if not cart_row:
        cursor.close()
        db.close()
        return '', 204

    cart_id = cart_row[0]

    # Step 1: Get quantity to restore
    cursor.execute('SELECT quantity FROM cart_items WHERE cart_id = %s AND id = %s', (cart_id, product_id))
    row = cursor.fetchone()
    if row:
        removed_qty = row[0]

        # Step 2: Update product quantity
        cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (removed_qty, product_id))

        # Step 3: Delete from cart_items
        cursor.execute('DELETE FROM cart_items WHERE cart_id = %s AND id = %s', (cart_id, product_id))

        # Step 4: If cart is now empty, delete the cart row
        cursor.execute('SELECT COUNT(*) FROM cart_items WHERE cart_id = %s', (cart_id,))
        item_count = cursor.fetchone()[0]
        if item_count == 0:
            cursor.execute('DELETE FROM cart WHERE cart_id = %s', (cart_id,))

        db.commit()

    cursor.close()
    db.close()
    return '', 204

@cart_bp.route('/update_qty/<int:product_id>', methods=['POST'])
def update_qty(product_id):
    user_id = session.get('user_id')
    new_qty = int(request.get_json().get('qty'))
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    if cart_row:
        cart_id = cart_row[0]

        # Fetch old quantity from cart_items
        cursor.execute('SELECT quantity FROM cart_items WHERE cart_id = %s AND id = %s', (cart_id, product_id))
        old_qty_row = cursor.fetchone()
        old_qty = old_qty_row[0] if old_qty_row else 0

        # Update cart_items
        cursor.execute('UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND id = %s',
                       (new_qty, cart_id, product_id))

        # Update products table
        qty_diff = old_qty - new_qty
        cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (qty_diff, product_id))

        db.commit()

    cursor.close()
    db.close()
    return '', 204

@cart_bp.route('/checkout')
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Step 1: Get cart_id and cart items
    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    if not cart_row:
        cursor.close()
        db.close()
        return "<h3>No items in cart to checkout.</h3>"

    cart_id = cart_row['cart_id']
    cursor.execute('''
        SELECT ci.id, ci.quantity, p.price
        FROM cart_items ci
        JOIN products p ON ci.id = p.id
        WHERE ci.cart_id = %s
    ''', (cart_id,))
    items = cursor.fetchall()

    if not items:
        cursor.close()
        db.close()
        return "<h3>Cart is empty.</h3>"

    # Step 2: Calculate total
    total = sum(item['price'] * item['quantity'] for item in items)
    bill_amount = total + 50  # add delivery charges

    # Step 3: Insert into orders table
    cursor.execute('''
        INSERT INTO orders (user_id, order_date, status, total)
        VALUES (%s, NOW(), %s, %s)
    ''', (user_id, 'Delivered', bill_amount))
    db.commit()
    order_id = cursor.lastrowid

    # Step 4: Insert into order_items table
    for item in items:
        cursor.execute('''
            INSERT INTO order_items (order_id, id, quantity, price)
            VALUES (%s, %s, %s, %s)
        ''', (order_id, item['id'], item['quantity'], item['price']))

    # Step 5: Delete from cart_items and cart
    cursor.execute('DELETE FROM cart_items WHERE cart_id = %s', (cart_id,))
    cursor.execute('DELETE FROM cart WHERE cart_id = %s', (cart_id,))
    db.commit()

    # Step 6: Prepare details for template
    delivery_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    
    cursor.close()
    db.close()

    return render_template('checkout.html',
                           user_name=session.get('user_name'),
                           order_id=order_id,
                           bill_amount=bill_amount,
                           delivery_date=delivery_date,
                           image_name='thankyou.png')  # You can change this name
