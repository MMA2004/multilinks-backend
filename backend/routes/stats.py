from flask import Blueprint, request, jsonify
import os
import json
import re
from datetime import datetime
from config import DATA_DIR

stats_bp = Blueprint('stats', __name__)

# ------ Helpers de ruta ------
_slug_re = re.compile(r"[^a-zA-Z0-9._-]")

def safe_slug(name: str) -> str:
    """Sanea el subdominio para usarlo como nombre de carpeta."""
    if not name:
        return "desconocido"
    return _slug_re.sub("-", name.strip())[:80]  # límite por si acaso

def _subdir(subdominio: str) -> str:
    return os.path.join(DATA_DIR, safe_slug(subdominio))

def _file_visitas(subdominio: str) -> str:
    return os.path.join(_subdir(subdominio), "visitas.json")

def _file_clicks(subdominio: str) -> str:
    return os.path.join(_subdir(subdominio), "clicks.json")

def _leer_lista(path: str):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                return []
            return json.loads(txt)
    except Exception:
        return []

def _guardar_lista(path: str, lista):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def guardar_evento_en(kind: str, subdominio: str, data: dict):
    """kind: 'visitas' | 'clicks'"""
    path = _file_visitas(subdominio) if kind == "visitas" else _file_clicks(subdominio)
    lista = _leer_lista(path)
    lista.append(data)
    _guardar_lista(path, lista)
    print(f"✅ {kind} -> {os.path.abspath(path)} (total={len(lista)})")

# ----- Endpoints -----
@stats_bp.route('/registro-visita', methods=['POST'])
def registro_visita():
    body = request.get_json(silent=True) or {}
    subdominio = body.get("subdominio") or body.get("subdomain") or "desconocido"
    body["timestamp"] = datetime.utcnow().isoformat()
    try:
        guardar_evento_en("visitas", subdominio, body)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@stats_bp.route('/registro-click', methods=['POST'])
def registro_click():
    body = request.get_json(silent=True) or {}
    subdominio = body.get("subdominio") or body.get("subdomain") or "desconocido"
    body["timestamp"] = datetime.utcnow().isoformat()
    try:
        guardar_evento_en("clicks", subdominio, body)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@stats_bp.route('/stats/<path:subdominio>', methods=['GET'])
def estadisticas_subdominio(subdominio):
    try:
        visitas = _leer_lista(_file_visitas(subdominio))
        clicks = _leer_lista(_file_clicks(subdominio))

        # (Opcional) Garantiza consistencia del filtro si en algún momento vinieron mal marcados
        visitas_filtradas = [v for v in visitas if v.get('subdominio') == subdominio or not v.get('subdominio')]
        clicks_filtrados = [c for c in clicks if c.get('subdominio') == subdominio or not c.get('subdominio')]

        mes = request.args.get('mes')
        if mes:
            visitas_filtradas = [v for v in visitas_filtradas if v.get('timestamp', '').startswith(mes)]
            clicks_filtrados = [c for c in clicks_filtrados if c.get('timestamp', '').startswith(mes)]

        clicks_por_boton = {}
        for c in clicks_filtrados:
            b = c.get('boton', 'desconocido')
            clicks_por_boton[b] = clicks_por_boton.get(b, 0) + 1

        return jsonify({
            "subdominio": subdominio,
            "visitas_totales": len(visitas_filtradas),
            "clicks_totales": len(clicks_filtrados),
            "clicks_por_boton": clicks_por_boton,
            "ultimas_visitas": visitas_filtradas[-10:],
            "ultimos_clicks": clicks_filtrados[-10:]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
