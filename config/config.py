"""
Configuración principal de la aplicación Hotel Paraíso Real
===========================================================

Este módulo contiene las configuraciones principales de la aplicación Flask.

Author: Equipo Hotel Paraíso Real
Version: 2.0
"""

import os

class Config:
    """
    Clase de configuración para la aplicación Flask.
    Contiene las variables necesarias para la configuración del sistema.
    """
    # Clave secreta para proteger formularios y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'

    # URI de la base de datos (SQLite)
    # La base de datos se creará automáticamente en el directorio del proyecto
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'reservas_hoteles.db')

    # Desactivamos las notificaciones de cambios en SQLAlchemy (mejora el rendimiento)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
