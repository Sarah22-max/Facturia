from flask import Flask, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
CORS(app)

# Configuration
IS_PRODUCTION = os.getenv('RENDER') or os.getenv('HEROKU_APP_NAME')
app.config['DEBUG'] = not IS_PRODUCTION and os.getenv('DEBUG', 'True').lower() == 'true'
app.url_map.strict_slashes = False  # Désactiver le contrôle strict des slashes

# Importer les routes
from routes import invoice_routes

# Enregistrer les blueprints
app.register_blueprint(invoice_routes.bp)

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de vérification de santé"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
