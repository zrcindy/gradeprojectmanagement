from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
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

# Define a route for the homepage
@app.route('/')
def hello_world():
    # Render the HTML template
    return render_template('index.html')

@app.route('/ingresar-propuesta', methods=['GET', 'POST'])
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
def ingresar_proyecto():
    # Render the HTML template
    return render_template('ingresar-proyecto.html')

@app.route('/ingresar-informe-final')
def ingresar_informe_final():
    # Render the HTML template
    return render_template('ingresar-informe-final.html')

@app.route('/consultar-proyecto')
def consultar_proyecto():
    # Render the HTML template
    return render_template('consultar-proyecto.html')

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
