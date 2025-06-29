#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

def crear_usuarios_prueba():
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existen usuarios
        admin_existente = Usuario.query.filter_by(email='admin@hotel.com').first()
        empleado_existente = Usuario.query.filter_by(email='empleado@hotel.com').first()
        
        usuarios_creados = []
        
        # Crear admin si no existe
        if not admin_existente:
            admin = Usuario(
                nombre='Admin Principal',
                email='admin@hotel.com',
                contraseña=generate_password_hash('admin123'),
                rol='admin'
            )
            db.session.add(admin)
            usuarios_creados.append('Admin: admin@hotel.com / admin123')
        
        # Crear empleado si no existe
        if not empleado_existente:
            empleado = Usuario(
                nombre='María Empleada',
                email='empleado@hotel.com',
                contraseña=generate_password_hash('empleado123'),
                rol='empleado'
            )
            db.session.add(empleado)
            usuarios_creados.append('Empleado: empleado@hotel.com / empleado123')
        
        # Crear cliente si no existe
        cliente_existente = Usuario.query.filter_by(email='cliente@hotel.com').first()
        if not cliente_existente:
            cliente = Usuario(
                nombre='Juan Cliente',
                email='cliente@hotel.com',
                contraseña=generate_password_hash('cliente123'),
                rol='cliente'
            )
            db.session.add(cliente)
            usuarios_creados.append('Cliente: cliente@hotel.com / cliente123')
        
        try:
            db.session.commit()
            print("✅ Usuarios de prueba creados exitosamente:")
            for usuario in usuarios_creados:
                print(f"   - {usuario}")
            
            if not usuarios_creados:
                print("ℹ️  Los usuarios de prueba ya existían en la base de datos")
                print("   - Admin: admin@hotel.com / admin123")
                print("   - Empleado: empleado@hotel.com / empleado123") 
                print("   - Cliente: cliente@hotel.com / cliente123")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuarios: {e}")

if __name__ == '__main__':
    crear_usuarios_prueba()
