from flask import Flask
from flask_cors import CORS
from routes.generate import generate_bp
from routes.stats import stats_bp
from routes.formularios import formularios_bp
from routes.delete_multilink import delete_bp
from routes.suspend_multilink import suspend_bp

app = Flask(__name__)
CORS(
app,
    resources={r"/api/*": {"origins": "*"}},  # <- permite cualquier origen
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    supports_credentials=False,
    max_age=86400,
)
app.config['API_SECRET'] = 'mi_super_token_123'
app.register_blueprint(generate_bp, url_prefix='/api')
app.register_blueprint(stats_bp, url_prefix='/api')
app.register_blueprint(formularios_bp, url_prefix='/api')
app.register_blueprint(delete_bp, url_prefix='/api')
app.register_blueprint(suspend_bp, url_prefix='/api')

if __name__ == '__main__':
    # Cambia host a 0.0.0.0 para que sea accesible desde fuera
    app.run(debug=True, host='0.0.0.0', port=5000)
