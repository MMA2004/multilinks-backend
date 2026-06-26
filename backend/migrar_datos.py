import os
import json
import sqlite3
from config import DATA_DIR
from utils.db import get_db_connection

def migrar_datos():
    print("Iniciando migración de datos JSON a SQLite...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_visitas = 0
    total_clicks = 0
    
    # Recorrer todas las carpetas dentro de DATA_DIR
    for item in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(folder_path):
            subdominio = item
            
            # Migrar visitas
            visitas_file = os.path.join(folder_path, "visitas.json")
            if os.path.exists(visitas_file):
                try:
                    with open(visitas_file, 'r', encoding='utf-8') as f:
                        visitas = json.load(f)
                        for v in visitas:
                            fecha = v.get('timestamp', '') or v.get('fecha', '')
                            user_agent = v.get('userAgent', '')
                            referrer = v.get('referrer', '')
                            cursor.execute(
                                'INSERT INTO visitas (subdominio, fecha, user_agent, referrer) VALUES (?, ?, ?, ?)',
                                (subdominio, fecha, user_agent, referrer)
                            )
                            total_visitas += 1
                except Exception as e:
                    print(f"Error procesando visitas de {subdominio}: {e}")
                    
            # Migrar clicks
            clicks_file = os.path.join(folder_path, "clicks.json")
            if os.path.exists(clicks_file):
                try:
                    with open(clicks_file, 'r', encoding='utf-8') as f:
                        clicks = json.load(f)
                        for c in clicks:
                            fecha = c.get('timestamp', '') or c.get('fecha', '')
                            boton = c.get('boton', 'desconocido')
                            cursor.execute(
                                'INSERT INTO clicks (subdominio, boton, fecha) VALUES (?, ?, ?)',
                                (subdominio, boton, fecha)
                            )
                            total_clicks += 1
                except Exception as e:
                    print(f"Error procesando clicks de {subdominio}: {e}")
                    
    conn.commit()
    conn.close()
    print(f"Migración completada. Se migraron {total_visitas} visitas y {total_clicks} clicks.")
    print("Nota: Los archivos .json originales no han sido eliminados por seguridad. Puedes eliminarlos manualmente cuando lo desees.")

if __name__ == '__main__':
    migrar_datos()
