import os
from app import create_app, db

print("Iniciando recreación de base de datos...")

# Crear app
app = create_app()

with app.app_context():
    # Eliminar archivo de BD si existe
    db_file = "reservas_hoteles.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print("✅ Base de datos anterior eliminada")
    
    # Crear todas las tablas
    db.create_all()
    print("✅ Base de datos recreada con esquema actualizado")
    
    print("🚀 ¡Listo! Ahora ejecuta 'python scripts/crear_usuarios.py' para agregar datos")
