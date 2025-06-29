import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🚀 Iniciando creación de usuarios...")
    
    from app import create_app, db
    from app.models import Usuario
    from werkzeug.security import generate_password_hash
    
    print("📦 Módulos importados correctamente")
    
    app = create_app()
    print("🏗️ Aplicación Flask creada")
    
    with app.app_context():
        print("🔗 Contexto de aplicación iniciado")
        
        # Verificar usuarios existentes
        total_usuarios = Usuario.query.count()
        print(f"👥 Usuarios existentes en la BD: {total_usuarios}")
        
        # Crear usuario empleado si no existe
        empleado_existente = Usuario.query.filter_by(email='empleado@hotel.com').first()
        
        if not empleado_existente:
            empleado = Usuario(
                nombre='Carlos Empleado',
                email='empleado@hotel.com',
                contraseña=generate_password_hash('empleado123'),
                rol='empleado'
            )
            db.session.add(empleado)
            db.session.commit()
            print("✅ Usuario empleado creado exitosamente")
        else:
            print("ℹ️ Usuario empleado ya existe")
        
        # Verificar admin
        admin_existente = Usuario.query.filter_by(email='admin@hotel.com').first()
        if not admin_existente:
            admin = Usuario(
                nombre='Admin Principal',
                email='admin@hotel.com',
                contraseña=generate_password_hash('admin123'),
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado exitosamente")
        else:
            print("ℹ️ Usuario admin ya existe")
            
        # Verificar cliente
        cliente_existente = Usuario.query.filter_by(email='cliente@hotel.com').first()
        if not cliente_existente:
            cliente = Usuario(
                nombre='María Cliente',
                email='cliente@hotel.com',
                contraseña=generate_password_hash('cliente123'),
                rol='cliente'
            )
            db.session.add(cliente)
            db.session.commit()
            print("✅ Usuario cliente creado exitosamente")
        else:
            print("ℹ️ Usuario cliente ya existe")
            
        print("\n" + "="*50)
        print("🎯 CREDENCIALES DE PRUEBA:")
        print("="*50)
        print("👑 ADMINISTRADOR:")
        print("   📧 Email: admin@hotel.com")
        print("   🔑 Contraseña: admin123")
        print()
        print("👔 EMPLEADO:")
        print("   📧 Email: empleado@hotel.com")
        print("   🔑 Contraseña: empleado123")
        print()
        print("👤 CLIENTE:")
        print("   📧 Email: cliente@hotel.com")
        print("   🔑 Contraseña: cliente123")
        print("="*50)
        
        total_final = Usuario.query.count()
        print(f"📊 Total usuarios en la BD: {total_final}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
