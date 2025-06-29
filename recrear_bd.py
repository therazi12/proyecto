#!/usr/bin/env python3
"""
Script simple para recrear la base de datos
"""
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash
import os

def recrear_bd():
    print("🔄 Recreando base de datos...")
    
    app = create_app()
    
    with app.app_context():
        # Eliminar BD existente
        if os.path.exists('reservas_hoteles.db'):
            os.remove('reservas_hoteles.db')
            print("✅ BD anterior eliminada")
        
        # Crear todas las tablas
        db.create_all()
        print("✅ BD recreada con esquema actualizado")
        
        # Crear usuario admin básico
        admin = Usuario(
            nombre="Administrador",
            email="admin@hotel.com",
            contraseña=generate_password_hash("admin123"),
            rol="admin"
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado (admin@hotel.com / admin123)")
        
        print("🚀 ¡Base de datos lista!")

if __name__ == "__main__":
    recrear_bd()
