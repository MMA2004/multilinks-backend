from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.db import get_db_connection

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/registro-visita', methods=['POST'])
def registro_visita():
    body = request.get_json(silent=True) or {}
    subdominio = body.get("subdominio") or body.get("subdomain") or "desconocido"
    user_agent = body.get("userAgent", "")
    referrer = body.get("referrer", "")
    fecha = datetime.utcnow().isoformat()
    
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO visitas (subdominio, fecha, user_agent, referrer) VALUES (?, ?, ?, ?)',
            (subdominio, fecha, user_agent, referrer)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@stats_bp.route('/registro-click', methods=['POST'])
def registro_click():
    body = request.get_json(silent=True) or {}
    subdominio = body.get("subdominio") or body.get("subdomain") or "desconocido"
    boton = body.get("boton", "desconocido")
    fecha = datetime.utcnow().isoformat()
    
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO clicks (subdominio, boton, fecha) VALUES (?, ?, ?)',
            (subdominio, boton, fecha)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@stats_bp.route('/stats/<path:subdominio>', methods=['GET'])
def estadisticas_subdominio(subdominio):
    try:
        conn = get_db_connection()
        
        # Filtro de mes
        mes = request.args.get('mes', '')
        
        # Visitas totales
        query_visitas = 'SELECT COUNT(*) FROM visitas WHERE subdominio = ?'
        params_visitas = [subdominio]
        if mes:
            query_visitas += ' AND fecha LIKE ?'
            params_visitas.append(f'{mes}%')
            
        visitas_totales = conn.execute(query_visitas, params_visitas).fetchone()[0]
        
        # Clicks totales
        query_clicks = 'SELECT COUNT(*) FROM clicks WHERE subdominio = ?'
        params_clicks = [subdominio]
        if mes:
            query_clicks += ' AND fecha LIKE ?'
            params_clicks.append(f'{mes}%')
            
        clicks_totales = conn.execute(query_clicks, params_clicks).fetchone()[0]
        
        # Clicks por botón
        query_group = 'SELECT boton, COUNT(*) as cantidad FROM clicks WHERE subdominio = ?'
        params_group = [subdominio]
        if mes:
            query_group += ' AND fecha LIKE ?'
            params_group.append(f'{mes}%')
        query_group += ' GROUP BY boton'
        
        clicks_por_boton_rows = conn.execute(query_group, params_group).fetchall()
        clicks_por_boton = {row['boton']: row['cantidad'] for row in clicks_por_boton_rows}
        
        # Referrers (Fuentes de Tráfico)
        query_ref = 'SELECT referrer, COUNT(*) as cantidad FROM visitas WHERE subdominio = ?'
        params_ref = [subdominio]
        if mes:
            query_ref += ' AND fecha LIKE ?'
            params_ref.append(f'{mes}%')
        query_ref += ' GROUP BY referrer ORDER BY cantidad DESC'
        
        visitas_por_referrer_rows = conn.execute(query_ref, params_ref).fetchall()
        visitas_por_referrer = { (row['referrer'] if row['referrer'] else 'Directo'): row['cantidad'] for row in visitas_por_referrer_rows }
        
        # Últimos registros
        ultimas_visitas = [dict(row) for row in conn.execute(
            'SELECT * FROM visitas WHERE subdominio = ? ORDER BY id DESC LIMIT 10', (subdominio,)
        ).fetchall()]
        
        ultimos_clicks = [dict(row) for row in conn.execute(
            'SELECT * FROM clicks WHERE subdominio = ? ORDER BY id DESC LIMIT 10', (subdominio,)
        ).fetchall()]
        
        conn.close()
        
        return jsonify({
            "subdominio": subdominio,
            "visitas_totales": visitas_totales,
            "clicks_totales": clicks_totales,
            "clicks_por_boton": clicks_por_boton,
            "visitas_por_referrer": visitas_por_referrer,
            "ultimas_visitas": ultimas_visitas,
            "ultimos_clicks": ultimos_clicks
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
