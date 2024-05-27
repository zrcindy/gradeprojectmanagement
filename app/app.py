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
app.config['UPLOAD_FOLDER_PURPOSES'] = '/app/uploads/purposes'
app.config['UPLOAD_FOLDER_PROJECTS'] = '/app/uploads/projects'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size: 16MB

# Ensure the upload folders exists
os.makedirs(app.config['UPLOAD_FOLDER_PURPOSES'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_PROJECTS'], exist_ok=True)

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
    connection = get_db_connection()
    cursor = connection.cursor()
    programas = []
    facultades = []

    try:
        cursor.execute("SELECT id, programa FROM Programas")
        programas = cursor.fetchall()
        cursor.execute("SELECT id, facultad FROM Facultades")
        facultades = cursor.fetchall()

        for row in facultades:
            print(row[1])

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
                    programa_id = request.form['programa']
                    # Process student field
                elif role == 'Evaluador':
                    facultad_id = request.form['facultad']
                    # Process Evaluador field

                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

                cursor.execute("INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
                            (username, hashed_password, role))
                user_id = cursor.lastrowid  # Get the auto-generated user ID
                
                # Insert user data into the appropriate table based on role
                if role == 'Estudiante':
                    cursor.execute("INSERT INTO Estudiantes (user_id, nombre, dni, email, programa_id) VALUES (%s, %s, %s, %s, %s)",
                                (user_id, name, dni, email, programa_id))
                elif role == 'Evaluador':
                    cursor.execute("INSERT INTO Evaluadores (user_id, nombre, dni, email, facultad_id) VALUES (%s, %s, %s, %s, %s)",
                                (user_id, name, dni, email, facultad_id))
                connection.commit()
                flash('¡Registro exitoso! Por favor inicie sesión.', 'success')
                return redirect(url_for('login'))
                
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return render_template('registro.html', programas=programas, facultades=facultades)

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
            flash('Ha iniciado correctamente.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
@role_required('Estudiante', 'Evaluador')
def profile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    user = None
    details = []
    programas = []
    facultades = []

    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            dni = request.form['dni']
            email = request.form['email']

            if session['role'] == 'Estudiante':
                programa_id = request.form['programa']
                cursor.execute("UPDATE Estudiantes SET nombre=%s, dni=%s, email=%s, programa_id=%s WHERE user_id=%s",
                               (nombre, dni, email, programa_id, session['user_id']))
            elif session['role'] == 'Evaluador':
                facultad_id = request.form['facultad']
                cursor.execute("UPDATE Evaluadores SET nombre=%s, dni=%s, email=%s, facultad_id=%s WHERE user_id=%s",
                               (nombre, dni, email, facultad_id, session['user_id']))

            connection.commit()
            flash('Profile updated successfully!', 'success')
        
        cursor.execute("SELECT * FROM Users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if user['role'] == 'Estudiante':
            cursor.execute("SELECT e.nombre, e.dni, e.email, p.programa FROM Estudiantes e JOIN Programas p ON e.programa_id = p.id WHERE user_id = %s", (session['user_id'],))
            details = cursor.fetchone()
            cursor.execute("SELECT * FROM Programas")
            programas = cursor.fetchall()
        elif user['role'] == 'Evaluador':
            cursor.execute("SELECT e.nombre, e.dni, e.email, f.facultad FROM Evaluadores e JOIN Facultades f ON e.facultad_id = f.id WHERE user_id = %s", (session['user_id'],))
            details = cursor.fetchone()
            cursor.execute("SELECT * from Facultades")
            facultades = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return render_template('profile.html', user=user, details=details, programas=programas, facultades=facultades)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión finalizada.', 'success')
    return redirect(url_for('login'))

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
            file_path = os.path.join(app.config['UPLOAD_FOLDER_PURPOSES'], filename)
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

@app.route('/ingresar-proyecto', methods=['GET', 'POST'])
@login_required
@role_required('Estudiante')
def ingresar_proyecto():
    if request.method == 'POST':
        if 'proyecto' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['proyecto']
        if file.filename == '':
            flash('No ha seleccionado un archivo', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER_PROJECTS'], filename)
            file.save(file_path)

            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO Proyectos (user_id, file_path) VALUES (%s, %s)",
                               (session['user_id'], file_path))
                connection.commit()
                flash('¡Proyecto cargado satisfactoriamente!', 'success')
            except mysql.connector.Error as err:
                flash(f'Error: {err}', 'danger')
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('consultar_proyecto'))
        else:
            flash('No pudo cargarse el Proyecto, asegúrese de subir un archivo con extensión .pdf', 'danger')




    # Render the HTML template
    return render_template('ingresar-proyecto.html')

@app.route('/consultar-proyecto')
@login_required
@role_required('Estudiante', 'Evaluador')
def consultar_proyecto():
    connection = get_db_connection()
    cursor = connection.cursor()
    proyectos = []
    try:
        if session['role'] == 'Estudiante':
            cursor.execute("SELECT p.id, p.file_path, u.username, e.nombre, e.email, e.dni, g.programa FROM Proyectos p JOIN Users u ON p.user_id = u.id JOIN Estudiantes e ON u.id = e.user_id JOIN Programas g ON g.id = e.programa_id WHERE u.id = %s", (session['user_id'],))
        elif session['role'] == 'Evaluador':
            cursor.execute("SELECT p.id, p.file_path, u.username, e.nombre, e.email, e.dni, g.programa FROM Proyectos p JOIN Users u ON p.user_id = u.id JOIN Estudiantes e ON u.id = e.user_id JOIN Programas g ON g.id = e.programa_id")
        proyectos = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
        proyectos = []
    finally:
        cursor.close()
        connection.close()
    # Render the HTML template
    return render_template('consultar-proyecto.html', proyectos=proyectos)

@app.route('/ver-propuestas', methods=['GET'])
@login_required
@role_required('Evaluador', 'Estudiante')
def ver_propuestas():
    connection = get_db_connection()
    cursor = connection.cursor()
    propuestas = []
    try:
        if session['role'] == 'Estudiante':
            cursor.execute("SELECT p.id, p.file_path, u.username, e.nombre, e.email, e.dni, g.programa FROM Propuestas p JOIN Users u ON p.user_id = u.id JOIN Estudiantes e ON u.id = e.user_id JOIN Programas g ON g.id = e.programa_id WHERE u.id = %s", (session['user_id'],))
        elif session['role'] == 'Evaluador':
            cursor.execute("SELECT p.id, p.file_path, u.username, e.nombre, e.email, e.dni, g.programa FROM Propuestas p JOIN Users u ON p.user_id = u.id JOIN Estudiantes e ON u.id = e.user_id JOIN Programas g ON g.id = e.programa_id")
        propuestas = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
        propuestas = []
    finally:
        cursor.close()
        connection.close()

    return render_template('ver-propuestas.html', propuestas=propuestas)

@app.route('/uploads/purposes/<filename>')
def uploaded_purpose(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PURPOSES'], filename)

@app.route('/uploads/projects/<filename>')
def uploaded_project(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PROJECTS'], filename)

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
