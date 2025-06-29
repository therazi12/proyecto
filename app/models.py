"""
Modelos de Base de Datos para el Sistema Hotelero - Hotel Paraíso Real
====================================================================

Este módulo contiene todos los modelos de datos usando SQLAlchemy.
Implementa el patrón Active Record para la gestión de entidades.

Autor: therazi12
Fecha: Junio 2025
Versión: 1.0
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


class Usuario(UserMixin, db.Model):
    """
    Modelo para gestionar usuarios del sistema.
    
    Roles disponibles:
    - admin: Administrador completo
    - empleado: Personal del hotel
    - cliente: Huéspedes del hotel
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)  # Aumentado para hash
    rol = db.Column(db.String(20), nullable=False, default='cliente')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Establece la contraseña hasheada para el usuario."""
        self.contraseña = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada es correcta."""
        return check_password_hash(self.contraseña, password)
    
    def __repr__(self):
        return f'<Usuario {self.email} - {self.rol}>'


class TipoHabitacion(db.Model):
    """
    Modelo para categorizar tipos de habitaciones.
    Ej: Simple, Doble, Suite, etc.
    """
    __tablename__ = 'tipos_habitacion'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    precio_base = db.Column(db.Float, nullable=False, default=0.0)
    capacidad_maxima = db.Column(db.Integer, default=2)
    
    # Relaciones
    habitaciones = db.relationship('Habitacion', backref='tipo', lazy=True)
    
    def __repr__(self):
        return f'<TipoHabitacion {self.nombre}>'


class Habitacion(db.Model):
    """
    Modelo para habitaciones individuales del hotel.
    """
    __tablename__ = 'habitaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_habitacion.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    disponible = db.Column(db.Boolean, default=True)
    capacidad = db.Column(db.Integer, default=2)
    imagen_url = db.Column(db.String(255))
    piso = db.Column(db.Integer)
    caracteristicas = db.Column(db.Text)  # JSON string con características
    
    # Relaciones
    reservas = db.relationship('Reserva', backref='habitacion', lazy=True)
    opiniones = db.relationship('Opinion', backref='habitacion', lazy=True)
    
    def __repr__(self):
        return f'<Habitacion {self.numero} - {self.tipo.nombre if self.tipo else "Sin tipo"}>'


# Tabla intermedia para la relación muchos a muchos entre Reserva y ServicioExtra
reserva_servicio = db.Table(
    'reserva_servicio',
    db.Column('reserva_id', db.Integer, db.ForeignKey('reservas.id'), primary_key=True),
    db.Column('servicio_id', db.Integer, db.ForeignKey('servicios_extra.id'), primary_key=True)
)


class ServicioExtra(db.Model):
    """
    Modelo para servicios adicionales del hotel.
    Ej: Spa, Restaurant, Lavandería, etc.
    """
    __tablename__ = 'servicios_extra'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    categoria = db.Column(db.String(50))  # 'spa', 'restaurant', 'transporte', etc.
    
    def __repr__(self):
        return f'<ServicioExtra {self.nombre} - ${self.precio}>'


class Reserva(db.Model):
    """
    Modelo para gestionar reservas de habitaciones.
    """
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    total = db.Column(db.Float, nullable=False, default=0.0)
    huespedes = db.Column(db.Integer, default=1)
    comentarios = db.Column(db.Text)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='reservas')
    servicios_extra = db.relationship('ServicioExtra', secondary=reserva_servicio, lazy='subquery',
                                    backref=db.backref('reservas', lazy=True))
    pagos = db.relationship('Pago', backref='reserva', lazy=True, cascade='all, delete-orphan')
    
    def calcular_total(self):
        """Calcula el total de la reserva incluyendo servicios extra."""
        dias = (self.fecha_fin - self.fecha_inicio).days
        total_habitacion = self.habitacion.precio * dias
        total_servicios = sum(servicio.precio for servicio in self.servicios_extra)
        return total_habitacion + total_servicios
    
    def __repr__(self):
        return f'<Reserva {self.id} - {self.usuario.nombre} - {self.estado}>'


class Pago(db.Model):
    """
    Modelo para gestionar pagos de reservas.
    """
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50), nullable=False)  # efectivo, tarjeta, transferencia
    estado = db.Column(db.String(20), default='completado')  # pendiente, completado, fallido
    referencia = db.Column(db.String(100))  # Número de transacción
    
    def __repr__(self):
        return f'<Pago {self.id} - ${self.monto} - {self.metodo}>'


class Promocion(db.Model):
    """
    Modelo para gestionar promociones y ofertas especiales.
    """
    __tablename__ = 'promociones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    descuento_porcentaje = db.Column(db.Float, default=0.0)  # 0-100
    descuento_fijo = db.Column(db.Float, default=0.0)  # Monto fijo
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    activa = db.Column(db.Boolean, default=True)
    codigo = db.Column(db.String(20), unique=True)  # Código promocional
    usos_maximos = db.Column(db.Integer)  # Límite de usos
    usos_actuales = db.Column(db.Integer, default=0)
    
    def es_valida(self):
        """Verifica si la promoción está vigente y disponible."""
        hoy = date.today()
        return (self.activa and 
                self.fecha_inicio <= hoy <= self.fecha_fin and
                (self.usos_maximos is None or self.usos_actuales < self.usos_maximos))
    
    def __repr__(self):
        return f'<Promocion {self.nombre} - {self.descuento_porcentaje}%>'


class Opinion(db.Model):
    """
    Modelo para gestionar opiniones y reseñas de clientes.
    """
    __tablename__ = 'opiniones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'))  # Opcional
    calificacion = db.Column(db.Integer, nullable=False)  # 1-5 estrellas
    comentario = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    aprobada = db.Column(db.Boolean, default=False)  # Moderación
    
    # Relación con usuario
    usuario = db.relationship('Usuario', backref='opiniones')
    
    def __repr__(self):
        return f'<Opinion {self.id} - {self.calificacion} estrellas - {self.usuario.nombre}>'
