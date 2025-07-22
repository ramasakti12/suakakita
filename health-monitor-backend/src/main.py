import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from src.models.user import db, User
from src.models.melon_pinter import MelonPinterData
from src.models.kangen_azi import KangenAziData
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.melon_pinter import melon_bp
from src.routes.kangen_azi import kangen_bp
from src.routes.export import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(melon_bp, url_prefix='/api/melon')
app.register_blueprint(kangen_bp, url_prefix='/api/kangen')
app.register_blueprint(export_bp, url_prefix='/api/export')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize scheduler
from src.utils.scheduler import init_scheduler
import atexit

scheduler = BackgroundScheduler()
scheduler.start()

# Initialize health monitor scheduler
health_scheduler = init_scheduler()

# Shutdown scheduler when app exits
def shutdown_scheduler():
    if health_scheduler:
        health_scheduler.shutdown()
    scheduler.shutdown()

atexit.register(shutdown_scheduler)

with app.app_context():
    db.create_all()
    # Create default users if they don't exist
    from src.utils.init_users import create_default_users
    create_default_users()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

