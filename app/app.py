from flask import Flask, render_template, request, flash, redirect, url_for, g, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import mysql.connector
import os

# Restricting file extensions
ALLOWED_EXTENSIONS = {'pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create a Flask application instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = '/app/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size: 16MB

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL Database configuration
db_config = {
    'user': 'userdba',
    'password': 'rut4lt3rn4',
#    'host': 'localhost',
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
            flash('Por favor inicie sesión para acceder a esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Por favor inicie sesión para acceder a esta página.', 'danger')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('No tienes permiso para acceder a esta página.', 'danger')
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
        name = request.form['name']
        dni = request.form['dni']
        email = request.form['email']
        role = request.form['role']

        if role not in ['Estudiante', 'Evaluador']:
            flash('Rol seleccionado Inválido', 'danger')
            return redirect(url_for('register'))
        
        if not username or not password or not role:
            flash('Todos los campos son requeridos!', 'danger')
        else:
            if role == 'Estudiante':
                programa = request.form['programa']
                # Process student field
            elif role == 'Evaluador':
                especialidad = request.form['especialidad']
                # Process jurado field

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
                            (username, hashed_password, role))
                user_id = cursor.lastrowid  # Get the auto-generated user ID
                
                # Insert user data into the appropriate table based on role
                if role == 'Estudiante':
                    cursor.execute("INSERT INTO Estudiantes (user_id, nombre, dni, email, programa) VALUES (%s, %s, %s, %s, %s)",
                                (user_id, name, dni, email, programa))
                elif role == 'Evaluador':
                    cursor.execute("INSERT INTO Evaluadores (user_id, nombre, dni, email, especialidad) VALUES (%s, %s, %s, %s, %s)",
                                (user_id, name, dni, email, especialidad))
                
                connection.commit()
                flash('¡Registro exitoso! Por favor inicie sesión.', 'success')
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
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Login satisfactorio!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión finalizada.', 'success')
    return redirect(url_for('home'))

@app.route('/ingresar-propuesta', methods=['GET', 'POST'])
@login_required
@role_required('Estudiante')
def ingresar_propuesta():
    if request.method == 'POST':
        if 'propuesta' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['propuesta']
        if file.filename == '':
            flash('No ha seleccionado un archivo', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO Propuestas (user_id, file_path) VALUES (%s, %s)",
                               (session['user_id'], file_path))
                connection.commit()
                flash('¡Propuesta cargada satisfactoriamente!', 'success')
            except mysql.connector.Error as err:
                flash(f'Error: {err}', 'danger')
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('ver_propuestas'))
        else:
            flash('No pudo cargarse la Propuesta, asegúrese de subir un archivo con extensión .pdf', 'danger')

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
@role_required('Estudiante', 'Evaluador')
def consultar_proyecto():
    # Render the HTML template
    return render_template('consultar-proyecto.html')

@app.route('/ver-propuestas')
@login_required
@role_required('Evaluador', 'Estudiante')
def ver_propuestas():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT p.id, p.file_path, u.username, e.nombre, e.email, e.dni FROM Propuestas p JOIN Users u ON p.user_id = u.id JOIN Estudiantes e ON u.id")
        propuestas = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
        propuestas = []
    finally:
        cursor.close()
        connection.close()

    return render_template('ver-propuestas.html', propuestas=propuestas)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
