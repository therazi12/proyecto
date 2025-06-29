"""
Inicialización de la aplicación Flask - Hotel Paraíso Real
=========================================================

Este módulo configura e inicializa la aplicación Flask junto con
todas sus extensiones y configuraciones.

Author: Equipo Hotel Paraíso Real
Version: 2.0
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Inicialización de extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """
    Función para cargar usuarios en Flask-Login.
    
    Args:
        user_id: ID del usuario a cargar
        
    Returns:
        Usuario correspondiente al ID
    """
    from app.models import Usuario  # Importa aquí para evitar el import circular
    return Usuario.query.get(int(user_id))

def create_app():
    """
    Factory function para crear la aplicación Flask.
    
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object('config.config.Config')

    # Configurar logging
    try:
        from config.logging_config import setup_logging
        setup_logging(app)
        app.logger.info("Logging configurado exitosamente")
    except ImportError:
        app.logger.warning("No se pudo configurar el logging avanzado")

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Corregir la referencia
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Importar modelos y blueprints después de inicializar la app
    from app import models
    from app.routes import main
    app.register_blueprint(main)
    
    # Registrar view helpers para templates
    try:
        from app.view_helpers import register_view_helpers
        register_view_helpers(app)
        app.logger.info("View helpers registrados exitosamente")
    except Exception as e:
        app.logger.warning(f"No se pudieron registrar los view helpers: {str(e)}")
    
    app.logger.info("Aplicación Flask inicializada correctamente")

    return app