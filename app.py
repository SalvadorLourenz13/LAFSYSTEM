from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB upload
app.secret_key = 'your_secret_key'  # Use a more secure secret key in production

# Admin credentials (for simplicity; ideally stored in a database)
admin_username = 'admin'
admin_password_hash = generate_password_hash('password123')  # Replace 'password123' with the actual password

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="lost_found"
)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Lost and Found Route
@app.route('/lost_found')
def lost_found():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('lost_found.html', items=items)

# Post Item Route
@app.route('/post_item', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        name = request.form['name']
        department = request.form['department']
        type = request.form['type']
        image = request.files['image']
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            cursor = db.cursor()
            cursor.execute("INSERT INTO items (title, category, name, department, image_path, type) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (title, category, name, department, filename, type))
            db.commit()
        return redirect(url_for('lost_found'))
    
    return render_template('post_item.html')

# About Us Route
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Us Route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        contact_no = request.form['contact_no']
        message = request.form['message']
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO messages (fullname, email, contact_no, message) VALUES (%s, %s, %s, %s)", 
                       (fullname, email, contact_no, message))
        db.commit()
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are correct
        if username == admin_username and check_password_hash(admin_password_hash, password):
            session['admin_logged_in'] = True
            flash('You are logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

# Admin Logout Route
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# Dashboard - List all posted items
@app.route('/admin_dashboard/items')
def admin_dashboard_items():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('admin_dashboard_items.html', items=items)

# Claimed/Unclaimed items section
@app.route('/admin_dashboard/status')
def admin_dashboard_claimed():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items WHERE claimed IS NOT NULL")
    claimed_items = cursor.fetchall()
    return render_template('admin_dashboard_claimed.html', items=claimed_items)

# Messages section
@app.route('/admin_dashboard/messages')
def admin_dashboard_messages():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    return render_template('admin_dashboard_messages.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
