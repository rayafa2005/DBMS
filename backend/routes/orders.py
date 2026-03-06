from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
import mysql.connector

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Raziya#2005',
        database='raziyadb',
        use_pure=True
    )

@orders_bp.route('/')
def view_orders():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    user_name = session.get('user_name', 'User')
    current_orders = []
    previous_orders = []

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch current orders (not Delivered)
        cursor.execute("""
            SELECT * FROM orders
            WHERE user_id = %s AND status != 'Delivered'
            ORDER BY order_date DESC
        """, (user_id,))
        current_orders = cursor.fetchall()

        # Clean old previous orders (delivered > 6 months ago)
        six_months_ago = datetime.now() - timedelta(days=180)
        cursor.execute("""
            DELETE FROM orders
            WHERE user_id = %s AND status = 'Delivered' AND order_date < %s
        """, (user_id, six_months_ago))
        connection.commit()

        # Fetch previous orders (Delivered)
        cursor.execute("""
            SELECT * FROM orders
            WHERE user_id = %s AND status = 'Delivered'
            ORDER BY order_date DESC
        """, (user_id,))
        previous_orders = cursor.fetchall()

        def fetch_order_items(order_list):
            for order in order_list:
                order_id = order.get('order_id')
                if not order_id:
                    print("⚠️ Order missing order_id:", order)
                    order['items'] = []
                    order['delivery_date'] = 'N/A'
                    order['total'] = float(order.get('total', 0))
                    continue

                cursor.execute("""
                    SELECT p.id, p.image FROM order_items oi
                    JOIN products p ON oi.id = p.id
                    WHERE oi.order_id = %s
                """, (order_id,))
                items = cursor.fetchall()
                order['items'] = items if items else []

                # Format delivery_date as 6 days after order_date
                order_date = order.get('order_date')
                if order_date:
                    delivery_dt = order_date + timedelta(days=6)
                    order['delivery_date'] = delivery_dt.strftime('%d %b %Y')
                else:
                    order['delivery_date'] = 'N/A'

                # Ensure total is float for formatting
                order['total'] = float(order.get('total', 0))

        fetch_order_items(current_orders)
        fetch_order_items(previous_orders)

    except mysql.connector.Error as e:
        print(f"❌ Error loading orders: {e}")
        return "<h3>Unable to load orders. Try again later.</h3>"
    except Exception as e:
        print(f"❌ Unexpected error loading orders: {e}")
        return "<h3>Unable to load orders. Try again later.</h3>"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template(
        'orders.html',
        user_name=user_name,
        current_orders=current_orders,
        previous_orders=previous_orders
    )
