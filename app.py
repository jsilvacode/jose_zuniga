from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Clave secreta para manejar sesiones

# Crear la carpeta para comprobantes si no existe
if not os.path.exists('comprobantes'):
    os.makedirs('comprobantes')

# Usuarios registrados (esto es solo un ejemplo básico; en un entorno real, usarías una base de datos)
usuarios_registrados = {
    'usuario': 'contraseña'  # Usuario y contraseña de ejemplo
}

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in usuarios_registrados and usuarios_registrados[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas, intente nuevamente.')
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Ruta para la página principal
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

# Ruta para procesar la solicitud de remesas
@app.route('/convert', methods=['POST'])
def convert():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        emisor = request.form['emisor']
        beneficiario = request.form['beneficiario']
        monto_chileno = float(request.form['monto'])
        comision = monto_chileno * 0.001  # 0.10%
        monto_final = monto_chileno - comision

        # Convertir a diferentes monedas
        tasa_dolar = 0.0012
        tasa_bolivar = 500
        tasa_euro = 0.001

        monto_dolares = monto_final * tasa_dolar
        monto_bolivares = monto_final * tasa_bolivar
        monto_euros = monto_final * tasa_euro

        # Generar comprobante
        comprobante_id = f"{session['username']}_{emisor}_{beneficiario}.txt"
        comprobante_path = os.path.join('comprobantes', comprobante_id)

        with open(comprobante_path, 'w') as f:
            f.write(f"Emisor: {emisor}\n")
            f.write(f"Beneficiario: {beneficiario}\n")
            f.write(f"Monto en pesos chilenos: {monto_chileno}\n")
            f.write(f"Comisión: {comision}\n")
            f.write(f"Monto en dólares: {monto_dolares}\n")
            f.write(f"Monto en bolívares: {monto_bolivares}\n")
            f.write(f"Monto en euros: {monto_euros}\n")

        flash('La solicitud ha sido procesada con éxito.')
        return render_template('result.html', dolares=monto_dolares, bolivares=monto_bolivares, euros=monto_euros, comision=comision, comprobante_id=comprobante_id)
    except ValueError:
        flash('Por favor, ingresa un monto válido.')
        return redirect(url_for('home'))

# Ruta para ver un comprobante
@app.route('/receipt/<comprobante_id>')
def receipt(comprobante_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    comprobante_path = os.path.join('comprobantes', comprobante_id)
    try:
        with open(comprobante_path, 'r') as f:
            contenido = f.read()
        return render_template('receipt.html', contenido=contenido)
    except FileNotFoundError:
        flash('Comprobante no encontrado.')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
