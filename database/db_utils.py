"""
Utilidad para verificar y gestionar la base de datos SQLite
"""
import sqlite3
import os
from app import create_app, db
from app.models import Usuario, Habitacion, Reserva, ServicioExtra, TipoHabitacion, Promocion, Opinion

def check_database():
    """Verifica el estado de la base de datos SQLite"""
    app = create_app()
    
    with app.app_context():
        db_path = os.path.join(os.path.dirname(__file__), 'reservas_hoteles.db')
        
        if not os.path.exists(db_path):
            print("❌ La base de datos no existe.")
            print("💡 Ejecuta 'python init_sqlite.py' para crearla.")
            return
        
        print("✅ Base de datos SQLite encontrada:")
        print(f"📁 Ubicación: {db_path}")
        print(f"📊 Tamaño: {os.path.getsize(db_path)} bytes")
        
        try:
            # Verificar contenido
            usuarios_count = Usuario.query.count()
            habitaciones_count = Habitacion.query.count()
            reservas_count = Reserva.query.count()
            servicios_count = ServicioExtra.query.count()
            tipos_count = TipoHabitacion.query.count()
            promociones_count = Promocion.query.count()
            opiniones_count = Opinion.query.count()
            
            print("\n📈 ESTADÍSTICAS DE LA BASE DE DATOS:")
            print(f"   👥 Usuarios: {usuarios_count}")
            print(f"   🏠 Habitaciones: {habitaciones_count}")
            print(f"   📋 Reservas: {reservas_count}")
            print(f"   🎯 Servicios Extra: {servicios_count}")
            print(f"   🏷️  Tipos de Habitación: {tipos_count}")
            print(f"   🎁 Promociones: {promociones_count}")
            print(f"   💬 Opiniones: {opiniones_count}")
            
            if usuarios_count > 0:
                print("\n👤 USUARIOS REGISTRADOS:")
                usuarios = Usuario.query.all()
                for usuario in usuarios:
                    print(f"   • {usuario.nombre} ({usuario.email}) - {usuario.rol}")
            
        except Exception as e:
            print(f"❌ Error al verificar la base de datos: {e}")

def reset_database():
    """Reinicia la base de datos eliminando el archivo"""
    db_path = os.path.join(os.path.dirname(__file__), 'reservas_hoteles.db')
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Base de datos eliminada.")
        print("💡 Ejecuta 'python init_sqlite.py' para crear una nueva.")
    else:
        print("❌ No se encontró archivo de base de datos para eliminar.")

def show_tables():
    """Muestra las tablas de la base de datos"""
    db_path = os.path.join(os.path.dirname(__file__), 'reservas_hoteles.db')
    
    if not os.path.exists(db_path):
        print("❌ La base de datos no existe.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 TABLAS EN LA BASE DE DATOS:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {table_name}: {count} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al consultar las tablas: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            check_database()
        elif command == "reset":
            reset_database()
        elif command == "tables":
            show_tables()
        else:
            print("❌ Comando no reconocido.")
            print("📖 Uso:")
            print("   python db_utils.py check   - Verificar base de datos")
            print("   python db_utils.py reset   - Eliminar base de datos")
            print("   python db_utils.py tables  - Mostrar tablas")
    else:
        check_database()
