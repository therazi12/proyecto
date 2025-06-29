"""
Script para inicializar la base de datos SQLite con datos de prueba
"""
from app import create_app, db
from app.models import (Usuario, TipoHabitacion, Habitacion, ServicioExtra, 
                       Promocion, Reserva, Opinion)
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import os

def init_sqlite_database():
    """Inicializa la base de datos SQLite con datos de prueba"""
    app = create_app()
    
    with app.app_context():
        # Eliminar base de datos existente si existe
        db_path = os.path.join(os.path.dirname(__file__), 'reservas_hoteles.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Base de datos anterior eliminada.")
        
        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente en SQLite.")
        
        print("Inicializando base de datos con datos de prueba...")
        
        # Crear usuarios
        usuarios = [
            Usuario(
                nombre="Administrador del Sistema",
                email="admin@hotel.com",
                contraseña=generate_password_hash("Admin123"),
                rol="admin"
            ),
            Usuario(
                nombre="María García - Empleada",
                email="empleado@hotel.com",
                contraseña=generate_password_hash("Empleado123"),
                rol="empleado"
            ),
            Usuario(
                nombre="Juan Pérez",
                email="cliente@hotel.com",
                contraseña=generate_password_hash("Cliente123"),
                rol="cliente"
            ),
            Usuario(
                nombre="Ana López",
                email="ana.lopez@email.com",
                contraseña=generate_password_hash("Cliente123"),
                rol="cliente"
            ),
            Usuario(
                nombre="Carlos Rodríguez",
                email="carlos.rodriguez@email.com",
                contraseña=generate_password_hash("Cliente123"),
                rol="cliente"
            )
        ]
        
        for usuario in usuarios:
            db.session.add(usuario)
        
        # Crear tipos de habitación
        tipos_habitacion = [
            TipoHabitacion(
                nombre="Estándar",
                descripcion="Habitación cómoda con servicios básicos, ideal para estadías cortas"
            ),
            TipoHabitacion(
                nombre="Deluxe",
                descripcion="Habitación espaciosa con servicios premium y vista panorámica"
            ),
            TipoHabitacion(
                nombre="Suite",
                descripcion="Suite de lujo con sala separada y amenidades exclusivas"
            ),
            TipoHabitacion(
                nombre="Suite Presidencial",
                descripcion="La mejor suite del hotel con todos los lujos y servicios VIP"
            )
        ]
        
        for tipo in tipos_habitacion:
            db.session.add(tipo)
        
        db.session.commit()  # Commit para obtener los IDs
        
        # Crear habitaciones
        habitaciones = [
            # Habitaciones Estándar
            Habitacion(numero="101", tipo="Simple", precio=50.0, descripcion="Habitación simple estándar con cama individual", disponible=True, tipo_id=1),
            Habitacion(numero="102", tipo="Simple", precio=50.0, descripcion="Habitación simple estándar con cama individual", disponible=True, tipo_id=1),
            Habitacion(numero="103", tipo="Doble", precio=65.0, descripcion="Habitación doble estándar con dos camas", disponible=True, tipo_id=1),
            Habitacion(numero="104", tipo="Doble", precio=65.0, descripcion="Habitación doble estándar con cama matrimonial", disponible=True, tipo_id=1),
            
            # Habitaciones Deluxe
            Habitacion(numero="201", tipo="Doble", precio=80.0, descripcion="Habitación doble deluxe con vista al jardín", disponible=True, tipo_id=2),
            Habitacion(numero="202", tipo="Doble", precio=85.0, descripcion="Habitación doble deluxe con vista al mar", disponible=True, tipo_id=2),
            Habitacion(numero="203", tipo="Triple", precio=100.0, descripcion="Habitación deluxe para tres personas", disponible=True, tipo_id=2),
            
            # Suites
            Habitacion(numero="301", tipo="Suite", precio=150.0, descripcion="Suite con vista al mar y sala de estar", disponible=True, tipo_id=3),
            Habitacion(numero="302", tipo="Suite", precio=140.0, descripcion="Suite con vista al jardín y balcón privado", disponible=True, tipo_id=3),
            Habitacion(numero="303", tipo="Suite", precio=160.0, descripcion="Suite familiar con dos habitaciones", disponible=True, tipo_id=3),
            
            # Suite Presidencial
            Habitacion(numero="401", tipo="Suite Presidencial", precio=300.0, descripcion="Suite presidencial con jacuzzi y terraza privada", disponible=True, tipo_id=4),
        ]
        
        for habitacion in habitaciones:
            db.session.add(habitacion)
        
        # Crear servicios extra
        servicios_extra = [
            ServicioExtra(nombre="Desayuno Buffet", descripcion="Desayuno buffet internacional con productos frescos", precio=15.0),
            ServicioExtra(nombre="WiFi Premium", descripcion="Internet de alta velocidad sin límites", precio=5.0),
            ServicioExtra(nombre="Spa Completo", descripcion="Acceso al spa con masajes y tratamientos", precio=50.0),
            ServicioExtra(nombre="Gimnasio 24/7", descripcion="Acceso completo al gimnasio las 24 horas", precio=10.0),
            ServicioExtra(nombre="Servicio de Lavandería", descripcion="Lavado y planchado de ropa", precio=20.0),
            ServicioExtra(nombre="Minibar Premium", descripcion="Minibar completamente surtido con bebidas premium", precio=25.0),
            ServicioExtra(nombre="Transfer Aeropuerto", descripcion="Transporte privado desde/hacia el aeropuerto", precio=30.0),
            ServicioExtra(nombre="Room Service 24h", descripcion="Servicio a la habitación las 24 horas", precio=8.0),
            ServicioExtra(nombre="Excursiones", descripcion="Tours guiados por la ciudad y alrededores", precio=40.0),
            ServicioExtra(nombre="Parking Privado", descripcion="Estacionamiento privado y seguro", precio=12.0),
        ]
        
        for servicio in servicios_extra:
            db.session.add(servicio)
        
        # Crear promociones
        promociones = [
            Promocion(
                descripcion="Descuento de temporada baja - Enero a Marzo",
                descuento=20.0,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 3, 31)
            ),
            Promocion(
                descripcion="Oferta fin de semana - Viernes a Domingo",
                descuento=15.0,
                fecha_inicio=date(2025, 6, 1),
                fecha_fin=date(2025, 12, 31)
            ),
            Promocion(
                descripcion="Descuento estancia larga - Más de 7 días",
                descuento=25.0,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 12, 31)
            ),
            Promocion(
                descripcion="Promoción de verano - Julio y Agosto",
                descuento=18.0,
                fecha_inicio=date(2025, 7, 1),
                fecha_fin=date(2025, 8, 31)
            ),
            Promocion(
                descripcion="Descuento familiar - Para familias con niños",
                descuento=12.0,
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 12, 31)
            )
        ]
        
        for promocion in promociones:
            db.session.add(promocion)
        
        db.session.commit()
        
        # Crear algunas reservas de ejemplo
        reservas = [
            Reserva(
                usuario_id=3,  # Juan Pérez
                habitacion_id=1,  # Habitación 101
                fecha_inicio=date(2025, 7, 15),
                fecha_fin=date(2025, 7, 18),
                estado="confirmada"
            ),
            Reserva(
                usuario_id=4,  # Ana López
                habitacion_id=5,  # Habitación 201
                fecha_inicio=date(2025, 8, 1),
                fecha_fin=date(2025, 8, 5),
                estado="pendiente"
            ),
            Reserva(
                usuario_id=5,  # Carlos Rodríguez
                habitacion_id=8,  # Suite 301
                fecha_inicio=date(2025, 9, 10),
                fecha_fin=date(2025, 9, 15),
                estado="confirmada"
            )
        ]
        
        for reserva in reservas:
            db.session.add(reserva)
        
        db.session.commit()
        
        # Asociar servicios a reservas
        reserva1 = Reserva.query.get(1)
        reserva1.servicios.append(ServicioExtra.query.get(1))  # Desayuno
        reserva1.servicios.append(ServicioExtra.query.get(2))  # WiFi
        
        reserva2 = Reserva.query.get(2)
        reserva2.servicios.append(ServicioExtra.query.get(1))  # Desayuno
        reserva2.servicios.append(ServicioExtra.query.get(3))  # Spa
        reserva2.servicios.append(ServicioExtra.query.get(7))  # Transfer
        
        reserva3 = Reserva.query.get(3)
        reserva3.servicios.append(ServicioExtra.query.get(1))  # Desayuno
        reserva3.servicios.append(ServicioExtra.query.get(6))  # Minibar
        reserva3.servicios.append(ServicioExtra.query.get(8))  # Room Service
        
        # Crear opiniones de ejemplo
        opiniones = [
            Opinion(
                usuario_id=3,
                habitacion_id=1,
                comentario="Excelente servicio y habitación muy limpia. El personal fue muy amable.",
                calificacion=5,
                fecha=datetime.now()
            ),
            Opinion(
                usuario_id=4,
                habitacion_id=5,
                comentario="Muy buena experiencia, la vista es hermosa. Volveré pronto.",
                calificacion=4,
                fecha=datetime.now()
            ),
            Opinion(
                usuario_id=5,
                habitacion_id=8,
                comentario="La suite es espectacular, muy cómoda y bien equipada.",
                calificacion=5,
                fecha=datetime.now()
            )
        ]
        
        for opinion in opiniones:
            db.session.add(opinion)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 BASE DE DATOS SQLITE INICIALIZADA EXITOSAMENTE! 🎉")
        print("="*60)
        print(f"📁 Archivo de base de datos: {db_path}")
        print(f"📊 Tablas creadas: {len(db.metadata.tables)}")
        print("\n👥 USUARIOS CREADOS:")
        print("┌─────────────────────────────────────────────────────────┐")
        print("│ Email                    │ Contraseña   │ Rol           │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│ admin@hotel.com          │ Admin123     │ Administrador │")
        print("│ empleado@hotel.com       │ Empleado123  │ Empleado      │")
        print("│ cliente@hotel.com        │ Cliente123   │ Cliente       │")
        print("│ ana.lopez@email.com      │ Cliente123   │ Cliente       │")
        print("│ carlos.rodriguez@email.com│ Cliente123   │ Cliente       │")
        print("└─────────────────────────────────────────────────────────┘")
        print("\n📋 ESTADÍSTICAS:")
        print(f"   • {len(usuarios)} usuarios")
        print(f"   • {len(tipos_habitacion)} tipos de habitación")
        print(f"   • {len(habitaciones)} habitaciones")
        print(f"   • {len(servicios_extra)} servicios extra")
        print(f"   • {len(promociones)} promociones")
        print(f"   • {len(reservas)} reservas de ejemplo")
        print(f"   • {len(opiniones)} opiniones")
        print("\n🚀 Para iniciar la aplicación ejecuta: python run.py")
        print("="*60)

if __name__ == "__main__":
    init_sqlite_database()
