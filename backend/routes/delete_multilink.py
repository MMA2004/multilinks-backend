from flask import Blueprint, request, jsonify
import os, shutil, re
from config import USUARIOS_DIR

delete_bp = Blueprint("delete_bp", __name__)

BASE_DIR = USUARIOS_DIR

SLUG_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])$')

@delete_bp.route("/multilinks/<slug>", methods=["DELETE", "OPTIONS"])
def delete_multilink(slug):
    # Preflight CORS (lo maneja Flask-CORS, pero respondemos 204 por claridad)
    if request.method == "OPTIONS":
        return ("", 204)

    # Validación de slug
    if not SLUG_RE.match(slug or ""):
        return jsonify({"error": "slug_invalido"}), 400

    # Construcción segura de ruta: evita path traversal
    target = os.path.realpath(os.path.join(BASE_DIR, slug))
    base_real = os.path.realpath(BASE_DIR)
    if not target.startswith(base_real + os.sep):
        return jsonify({"error": "ruta_insegura"}), 400

    if not os.path.exists(target):
        return jsonify({"ok": True, "deleted": slug, "note": "folder_not_found"}), 200

    try:
        shutil.rmtree(target)
        return jsonify({"ok": True, "deleted": slug}), 200
    except PermissionError as e:
        return jsonify({"error": "permission_denied", "detail": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "server_error", "detail": str(e)}), 500
