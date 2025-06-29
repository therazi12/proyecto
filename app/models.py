from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(60), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'admin', 'empleado', 'cliente'

class TipoHabitacion(db.Model):
    __tablename__ = 'tipos_habitacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    imagen_url = db.Column(db.String(255))  # URL de imagen por defecto para este tipo

    habitaciones = db.relationship('Habitacion', backref='tipo_hab')

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # simple, doble, suite, etc.
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    disponible = db.Column(db.Boolean, default=True)
    capacidad = db.Column(db.Integer, default=2)  # Número máximo de huéspedes
    imagen_url = db.Column(db.String(255))  # URL de la imagen principal
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_habitacion.id'), nullable=False)

class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False)
    metodo = db.Column(db.String(50), nullable=False)  # efectivo, tarjeta, etc.

    reserva = db.relationship('Reserva', backref='pagos')

# Tabla intermedia para la relación muchos a muchos
reserva_servicio = db.Table(
    'reserva_servicio',
    db.Column('reserva_id', db.Integer, db.ForeignKey('reservas.id'), primary_key=True),
    db.Column('servicio_id', db.Integer, db.ForeignKey('servicios_extra.id'), primary_key=True)
)

class ServicioExtra(db.Model):
    __tablename__ = 'servicios_extra'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Float, nullable=False)

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada

    usuario = db.relationship('Usuario', backref='reservas')
    habitacion = db.relationship('Habitacion', backref='reservas')
    servicios = db.relationship('ServicioExtra', secondary=reserva_servicio, backref='reservas')

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)

    reserva = db.relationship('Reserva', backref='factura')

class HistorialAcceso(db.Model):
    __tablename__ = 'historial_acceso'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    accion = db.Column(db.String(100), nullable=False)
    usuario = db.relationship('Usuario', backref='historial_acceso')

class Promocion(db.Model):
    __tablename__ = 'promociones'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    descuento = db.Column(db.Float, nullable=False)  # porcentaje o monto
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

class Opinion(db.Model):
    __tablename__ = 'opiniones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    comentario = db.Column(db.String(255))
    calificacion = db.Column(db.Integer)  # 1 a 5 estrellas
    fecha = db.Column(db.DateTime, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)