"""
Configuración de logging para la aplicación Hotel Paraíso Real
==============================================================

Este módulo configura el sistema de logging para la aplicación,
incluyendo diferentes niveles y formatos de log.

Author: Equipo Hotel Paraíso Real
Version: 2.0
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app):
    """
    Configura el sistema de logging para la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Crear directorio de logs si no existe
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configurar formato de logs
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar handler para archivo general
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logs_dir, 'hotel_app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Configurar handler para errores
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logs_dir, 'hotel_errors.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configurar handler para consola (desarrollo)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configurar logger de la aplicación
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Evitar duplicación de logs
    app.logger.propagate = False
    
    # Registrar inicio de logging
    app.logger.info("Sistema de logging configurado exitosamente")
    app.logger.info(f"Aplicación iniciada en modo {'DEBUG' if app.debug else 'PRODUCCIÓN'}")

def get_logger(name):
    """
    Obtiene un logger configurado para un módulo específico.
    
    Args:
        name: Nombre del módulo
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
