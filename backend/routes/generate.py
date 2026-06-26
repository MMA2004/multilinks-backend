from flask import Blueprint, request, jsonify, current_app

from utils.generator import generar_pagina

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generar', methods=['POST'])
def generar():

    # Verificar token en header Authorization
    token = request.headers.get('Authorization', '')
    expected_token = f"Bearer {current_app.config['API_SECRET']}"
    if token != expected_token:
        return jsonify({"error": "No autorizado"}), 401


    data = request.json
    url = data.get("url")
    plantilla = data.get("plantilla", "plantilla_comercial")
    links = data.get("botones", [])

    if not url:
        return jsonify({"error": "Datos incompletos"}), 400

    # Ajustar data para enviar a generar_pagina
    data["botones"] = links

    ok = generar_pagina(data, plantilla)

    if ok:
        # Aquí asegúrate de que el dominio sea el correcto para tu configuración DNS y Nginx
        url_generada = f"https://{url.replace(' ', '-').lower()}.gibracompany.com"
        return jsonify({"url": url_generada})
    else:
        return jsonify({"error": "Error al generar la página"}), 500
