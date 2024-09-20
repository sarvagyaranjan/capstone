from flask import Flask, render_template, request, url_for, flash, session
from werkzeug.utils import redirect
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'many random bytes'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sr@15082002'
app.config['MYSQL_DB'] = 'crud'

def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Home Page Route
@app.route('/')
def home():
    return render_template('home.html')

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_out' in session:  # Check if the user just logged out
        flash("You have been logged out successfully.")
        session.pop('logged_out', None)  # Clear the session variable

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
        
        connection.close()

        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            flash("Login Successful!")
            return redirect(url_for('Index'))
        else:
            flash("Incorrect Username or Password")
            return redirect(url_for('login'))

    return render_template('login.html')

# Student List Page
@app.route('/students')
def Index():
    if 'loggedin' in session:
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM students")
            data = cur.fetchall()
        connection.close()
        return render_template('index.html', students=data)
    else:
        flash("Please login to view this page")
        return redirect(url_for('login'))

# Insert Student Route
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
            connection.commit()
        connection.close()
        return redirect(url_for('Index'))

# Delete Student Route
@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    connection = get_db_connection()
    with connection.cursor() as cur:
        cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
        connection.commit()
    connection.close()
    return redirect(url_for('Index'))

# Update Student Route
@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
            UPDATE students SET name=%s, email=%s, phone=%s
            WHERE id=%s
            """, (name, email, phone, id_data))
            connection.commit()
        connection.close()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    session['logged_out'] = True  # Set the logged out session variable
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == "__main__":
    app.run(debug=True)
