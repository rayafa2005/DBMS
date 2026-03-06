from flask import Blueprint, render_template, request, redirect, session, url_for, make_response, jsonify
from db import get_db

view_prd_bp = Blueprint('view_prd', __name__)

@view_prd_bp.route('/product/<int:product_id>', methods=['GET'])
def view_product(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        db.close()
        return "Product not found", 404

    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    cart_id = cart_row['cart_id'] if cart_row else None

    cursor.execute('SELECT 1 FROM wishlist WHERE user_id = %s AND id = %s', (user_id, product_id))
    in_wishlist = cursor.fetchone() is not None

    in_cart = False
    if cart_id:
        cursor.execute('SELECT 1 FROM cart_items WHERE cart_id = %s AND id = %s', (cart_id, product_id))
        in_cart = cursor.fetchone() is not None

    cursor.close()
    db.close()

    response = make_response(render_template(
        'view_prd.html',
        product=product,
        in_wishlist=in_wishlist,
        in_cart=in_cart,
        user_name=session.get('user_name')
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@view_prd_bp.route('/product/action/<int:product_id>', methods=['POST'])
def product_action(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        db.close()
        return jsonify({'error': 'Product not found'}), 404

    cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s', (user_id,))
    cart_row = cursor.fetchone()
    cart_id = cart_row['cart_id'] if cart_row else None

    data = request.get_json()
    action = data.get('action')

    if action == 'wishlist':
        cursor.execute('SELECT 1 FROM wishlist WHERE user_id = %s AND id = %s', (user_id, product_id))
        in_wishlist = cursor.fetchone() is not None
        if not in_wishlist:
            cursor.execute('INSERT INTO wishlist (user_id, id) VALUES (%s, %s)', (user_id, product_id))
            db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})

    elif action == 'cart':
        if product['quantity'] == 0:
            cursor.close()
            db.close()
            return jsonify({'error': 'Product is sold out'}), 400

        try:
            selected_qty = int(data.get('selected_qty', 1))
        except:
            selected_qty = 1

        if selected_qty > product['quantity']:
            cursor.close()
            db.close()
            return jsonify({'error': 'Quantity exceeds available stock'}), 400

        if not cart_id:
            cursor.execute('INSERT INTO cart (user_id, created_at) VALUES (%s, NOW())', (user_id,))
            db.commit()
            cursor.execute('SELECT cart_id FROM cart WHERE user_id = %s ORDER BY cart_id DESC LIMIT 1', (user_id,))
            cart_id = cursor.fetchone()['cart_id']

        # Check if product already in cart
        cursor.execute('SELECT quantity FROM cart_items WHERE cart_id = %s AND id = %s', (cart_id, product_id))
        row = cursor.fetchone()
        if row:
            # Update quantity (increment)
            new_qty = row['quantity'] + selected_qty
            if new_qty > product['quantity']:
                cursor.close()
                db.close()
                return jsonify({'error': 'Quantity exceeds available stock'}), 400

            cursor.execute('UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND id = %s',
                           (new_qty, cart_id, product_id))
        else:
            # Insert new item in cart
            cursor.execute('INSERT INTO cart_items (cart_id, id, quantity) VALUES (%s, %s, %s)',
                           (cart_id, product_id, selected_qty))

        # Deduct product quantity in inventory
        cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s',
                       (selected_qty, product_id))
        db.commit()

        # Fetch updated quantity
        cursor.execute('SELECT quantity FROM products WHERE id = %s', (product_id,))
        updated_qty = cursor.fetchone()['quantity']

        cursor.close()
        db.close()
        return jsonify({'success': True, 'remaining_quantity': updated_qty})

    else:
        cursor.close()
        db.close()
        return jsonify({'error': 'Invalid action'}), 400
