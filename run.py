# Importamos la función create_app desde el paquete app
from app import create_app, db
import os

# Creamos una instancia de la aplicación Flask
app = create_app()

if __name__ == "__main__":
    """
    Punto de entrada para ejecutar la aplicación Flask.
    Ejecutamos la aplicación en modo debug para facilitar el desarrollo.
    """
    with app.app_context():
        # Verificar si existe la base de datos
        db_path = os.path.join(os.path.dirname(__file__), 'reservas_hoteles.db')
        
        if not os.path.exists(db_path):
            print("⚠️  No se encontró la base de datos SQLite.")
            print("🔧 Creando estructura de base de datos...")
            db.create_all()
            print("✅ Estructura de base de datos creada.")
            print("💡 Para agregar datos de prueba, ejecuta: python init_sqlite.py")
        else:
            print("✅ Base de datos SQLite encontrada.")
            # Crear las tablas si no existen (por si se agregaron nuevas)
            db.create_all()
    
    # Configurar host y puerto
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    print("🏨 Hotel Paraíso Real - Sistema de Reservas")
    print("📊 Base de datos: SQLite")
    app.run(host=host, port=port, debug=debug)