from db import get_db
from flask import Flask, render_template, request, redirect, url_for, session
from routes.index import index_bp
from routes.profile import profile_bp
from routes.view_prd import view_prd_bp
from routes.cart import cart_bp
from routes.wishlist import wishlist_bp
from routes.orders import orders_bp
from routes.donate import donate_bp


import mysql.connector

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.secret_key = 'supersecretkey'
app.register_blueprint(index_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(view_prd_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(donate_bp)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST']) 
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            connection = get_db()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT user_id, name, email, password_hash FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            if user and user['password_hash'] == password:
                print("✅ Login successful.")
                session['user_id'] = user['user_id']  # Store user_id
                session['user_name'] = user['name'] 
                return redirect(url_for('index.index'))
            else:
                print("❌ Invalid credentials.")
                return "<h3>Invalid email or password. <a href='/login'>Try again</a>.</h3>"
        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")
            return "<h3>Database connection error.</h3>"
        finally:
              if connection.is_connected():
                   cursor.close()
                   connection.close()
    message = request.args.get('message')
    return render_template('login.html', message=message)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']
        phone = request.form['phone']

        if password != confirm_password:
            return "<h3>Passwords do not match. <a href='/signin'>Try again</a>.</h3>"

        try:
            connection = get_db()
            cursor = connection.cursor()

           # ✅ Fix applied here
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

            # ✅ Ensure no unread result remains
            while cursor.nextset():
                pass

            if result:
                cursor.close()
                connection.close()
                return redirect(url_for('login_page', message='exists'))

            # Insert new user
            insert_query = """
                INSERT INTO users (name, email, password_hash, address, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(insert_query, (name, email, password, address, phone))
            connection.commit()

            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]
            session['user_id'] = user_id
            session['user_name'] = name

            cursor.close()
            connection.close()
            return redirect(url_for('index.index'))

        except Exception as e:
            return f"<h3>Error: {e}</h3><a href='/signin'>Try again</a>"

    return render_template('signin.html')
@app.route('/logout.html')
def logout_page():
    session.clear()  # Clears all session data
    return render_template('logout.html')

if __name__ == '__main__':
    print("🚀 Starting Flask app...")
    app.run(debug=True)
