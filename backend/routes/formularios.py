from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
from config import DATA_DIR

formularios_bp = Blueprint('formularios', __name__)

FORMULARIOS_FILE = os.path.join(DATA_DIR, 'respuestas_formularios.json')

def guardar_respuesta(data):
    try:
        if os.path.exists(FORMULARIOS_FILE):
            with open(FORMULARIOS_FILE, 'r', encoding='utf-8') as f:
                lista = json.load(f)
        else:
            lista = []

        lista.append(data)
        with open(FORMULARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(lista, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("❌ Error guardando respuesta del formulario:", e)

@formularios_bp.route('/formulario/<url>', methods=['POST'])
def guardar_formulario_por_url(url):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    data['url'] = url
    data['timestamp'] = datetime.utcnow().isoformat()

    guardar_respuesta(data)

    return jsonify({"status": "ok"})

@formularios_bp.route('/ver-formularios/<url>', methods=['GET'])
def ver_formularios(url):
    try:
        if not os.path.exists(FORMULARIOS_FILE):
            return jsonify([])

        with open(FORMULARIOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Filtrar solo por la URL
        respuestas = [entry for entry in data if entry.get('url') == url]
        return jsonify(respuestas)
    except Exception as e:
        print("❌ Error al leer formularios:", e)
        return jsonify({"error": "Error interno del servidor"}), 500
