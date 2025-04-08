from flask import Flask, request, jsonify
from flask_cors import CORS  # Para evitar errores CORS con Android
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite peticiones desde tu app Android

# Configuración de la base de datos SQLite
DATABASE = 'data/mantenimiento.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para obtener diccionarios
    return conn

# Crear tabla si no existe
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zona TEXT NOT NULL,
            nota TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Ejecutar al iniciar la API

# Endpoint para guardar datos desde Android
@app.route('/api/guardar', methods=['POST'])
def guardar_registro():
    try:
        data = request.json
        zona = data.get('zona')
        nota = data.get('nota')

        if not zona or not nota:
            return jsonify({"error": "Zona y nota son requeridos"}), 400

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO registros (zona, nota, fecha) VALUES (?, ?, ?)',
            (zona, nota, fecha)
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Datos guardados"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener todos los registros
@app.route('/api/registros', methods=['GET'])
def obtener_registros():
    try:
        conn = get_db_connection()
        registros = conn.execute('SELECT * FROM registros').fetchall()
        conn.close()

        # Convertir registros a lista de diccionarios
        resultado = []
        for reg in registros:
            resultado.append({
                "id": reg["id"],
                "zona": reg["zona"],
                "nota": reg["nota"],
                "fecha": reg["fecha"]
            })

        return jsonify({"data": resultado})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    conn = sqlite3.connect('mantenimiento.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        return jsonify({'success': True, 'message': 'Registro eliminado'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error al eliminar', 'error': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)