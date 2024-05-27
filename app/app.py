from flask import Flask, render_template, request, flash, redirect, url_for, g, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import mysql.connector
import os

# Create a Flask application instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size: 16MB

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL Database configuration
db_config = {
    'user': 'userdba',
    'password': 'rut4lt3rn4',
    'host': 'db',
    'database': 'database_production',
    'raise_on_warnings': True
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Decorator to check if a user is logged in and has the correct role.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('login'))
            if session.get('role') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Define a route for the homepage
@app.route('/')
def home():
    # Render the HTML template
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if not username or not password or not role:
            flash('All fields are required!', 'danger')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                               (username, hashed_password, role))
                connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.Error as err:
                flash(f'Error: {err}', 'danger')
            finally:
                cursor.close()
                connection.close()
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/ingresar-propuesta', methods=['GET', 'POST'])
@login_required
@role_required('Estudiante')
def ingresar_propuesta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        file = request.files['propuesta']

        if not nombre or not email or not file:
            flash('Todos los campos son obligatorios', 'danger')
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save to database
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "INSERT INTO propuestas (nombre, email, filename) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, email, filename))
            connection.commit()
            cursor.close()
            connection.close()

            flash('Propuesta ingresada correctamente', 'success')
            return redirect(url_for('ingresar_propuesta'))

    # Render the HTML template
    return render_template('ingresar-propuesta.html')

@app.route('/ingresar-proyecto')
@login_required
@role_required('Estudiante')
def ingresar_proyecto():
    # Render the HTML template
    return render_template('ingresar-proyecto.html')

@app.route('/ingresar-informe-final')
@login_required
@role_required('Estudiante')
def ingresar_informe_final():
    # Render the HTML template
    return render_template('ingresar-informe-final.html')

@app.route('/consultar-proyecto')
@login_required
@role_required('Estudiante')
@role_required('Evaluador')
def consultar_proyecto():
    # Render the HTML template
    return render_template('consultar-proyecto.html')

@app.route('/ver-propuestas')
@login_required
@role_required('Evaluador')
def view_propuestas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM propuestas")
    propuestas = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('ver-propuestas.html', propuestas=propuestas)

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
