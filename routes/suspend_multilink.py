# routes/suspend_multilink.py
import os
import re
from flask import Blueprint, jsonify, request, current_app

suspend_bp = Blueprint("suspend_bp", __name__)

# Carpeta raíz donde guardas los sitios por subdominio
BASE_DIR = "/var/www/multilinks/usuarios"

# Slug seguro: a-z, 0-9 y guiones; 2-63 chars; sin guión al inicio/fin
SLUG_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$')

def validate_slug(slug: str) -> bool:
    return bool(SLUG_RE.match(slug or ""))

def user_root(slug: str) -> str:
    return os.path.join(BASE_DIR, slug)

def flag_path(slug: str) -> str:
    return os.path.join(BASE_DIR, slug, ".suspended")

def require_api_key():
    # Valida X-API-Key contra app.config['API_SECRET']
    api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
    secret = current_app.config.get("API_SECRET")
    if not secret or api_key != secret:
        return False
    return True

# -------- Endpoints -------- #

@suspend_bp.route("/multilinks/<slug>/status", methods=["GET", "OPTIONS"])
def suspension_status(slug):
    if request.method == "OPTIONS":
        return ("", 204)
    if not validate_slug(slug):
        return jsonify({"ok": False, "error": "slug inválido"}), 400
    suspended = os.path.isfile(flag_path(slug))
    return jsonify({"ok": True, "slug": slug, "suspended": suspended})

@suspend_bp.route("/multilinks/<slug>/suspend", methods=["POST", "OPTIONS"])
def suspend(slug):
    if request.method == "OPTIONS":
        return ("", 204)
    if not require_api_key():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    if not validate_slug(slug):
        return jsonify({"ok": False, "error": "slug inválido"}), 400

    try:
        os.makedirs(user_root(slug), exist_ok=True)
        # crear el flag
        with open(flag_path(slug), "w") as f:
            f.write("suspended\n")
        return jsonify({"ok": True, "slug": slug, "suspended": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@suspend_bp.route("/multilinks/<slug>/unsuspend", methods=["POST", "OPTIONS"])
def unsuspend(slug):
    if request.method == "OPTIONS":
        return ("", 204)
    if not require_api_key():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    if not validate_slug(slug):
        return jsonify({"ok": False, "error": "slug inválido"}), 400

    try:
        try:
            os.remove(flag_path(slug))
        except FileNotFoundError:
            pass
        return jsonify({"ok": True, "slug": slug, "suspended": False})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
