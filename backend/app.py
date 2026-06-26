from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Aseguramos que se cargan las variables de entorno
load_dotenv()

from routes.generate import generate_bp
from routes.stats import stats_bp
from routes.formularios import formularios_bp
from routes.delete_multilink import delete_bp
from routes.suspend_multilink import suspend_bp
from config import ROOT_DIR  # Esto asegura que las carpetas base se crean al inicio

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    supports_credentials=False,
    max_age=86400,
)

app.config['API_SECRET'] = os.getenv('API_SECRET', 'mi_super_token_123')

app.register_blueprint(generate_bp, url_prefix='/api')
app.register_blueprint(stats_bp, url_prefix='/api')
app.register_blueprint(formularios_bp, url_prefix='/api')
app.register_blueprint(delete_bp, url_prefix='/api')
app.register_blueprint(suspend_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
