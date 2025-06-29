#!/usr/bin/env python3
"""
Script para recrear la base de datos con el esquema actualizado
"""
import os
import sys

# Agregar el directorio padre al path para poder importar la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import *

def recrear_database():
    """Recrea la base de datos con el esquema actual"""
    app = create_app()
    
    with app.app_context():
        # Eliminar base de datos existente
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reservas_hoteles.db')
        
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Base de datos anterior eliminada: {db_path}")
        
        # Crear todas las tablas con el esquema actual
        db.create_all()
        print("✅ Nuevas tablas creadas con esquema actualizado")
        
        # Confirmar las tablas creadas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tablas creadas: {', '.join(tables)}")
        
        print("🚀 Base de datos recreada exitosamente")
        print("💡 Ahora puedes ejecutar crear_usuarios.py para agregar datos de prueba")

if __name__ == "__main__":
    recrear_database()
