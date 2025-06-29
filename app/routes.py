"""
Módulo de rutas (Controladores) - Capa de Control en el patrón MVC
===============================================================

Este módulo contiene todas las rutas y controladores de la aplicación Flask.
Los controladores se encargan de:
- Recibir las peticiones HTTP de los usuarios
- Validar los datos de entrada (usando utils y services)
- Interactuar con la capa de servicios para la lógica de negocio
- Renderizar las vistas correspondientes
- Manejar errores y logging

Arquitectura:
- Routes (este archivo): Controladores HTTP
- Services: Lógica de negocio y validaciones
- Models: Modelos de datos y acceso a base de datos
- Templates: Vistas (UI)

Author: Equipo Hotel Paraíso Real
Version: 2.0
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, Habitacion, TipoHabitacion, ServicioExtra, Reserva, reserva_servicio, Promocion, Opinion
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from datetime import datetime, date
from functools import wraps

# Importar servicios para lógica de negocio
try:
    from app.services import (
        UsuarioService, ReservaService, EstadisticasService, ValidacionService, PromocionService
    )
except ImportError:
    # Fallback en caso de que no existan los servicios
    logging.warning("No se pudieron importar los servicios. Usando lógica directa en controladores.")
    UsuarioService = ReservaService = EstadisticasService = ValidacionService = PromocionService = None

# Configurar logging para este módulo
logger = logging.getLogger(__name__)

# Definimos un blueprint para las rutas principales
main = Blueprint('main', __name__)

# =============================================================================
# DECORADORES DE AUTORIZACIÓN
# =============================================================================

def admin_required(f):
    """
    Decorador que requiere permisos de administrador.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada que verifica permisos de admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            logger.warning(f"Acceso denegado a {f.__name__} para usuario {current_user.email if current_user.is_authenticated else 'anónimo'}")
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_empleado_required(f):
    """
    Decorador que requiere permisos de administrador o empleado.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada que verifica permisos de admin o empleado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol not in ['admin', 'empleado']:
            logger.warning(f"Acceso denegado a {f.__name__} para usuario {current_user.email if current_user.is_authenticated else 'anónimo'}")
            flash('Acceso denegado. Se requieren permisos de administrador o empleado.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# RUTAS PRINCIPALES Y AUTENTICACIÓN
# =============================================================================

@main.route("/")
def home():
    """
    Controlador para la página principal de la aplicación.
    
    Returns:
        Template renderizado de la página de inicio
    """
    try:
        logger.info("Acceso a página principal")
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error en página principal: {str(e)}")
        flash('Error al cargar la página principal.', 'error')
        return render_template("index.html")  # Fallback

@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Controlador para el inicio de sesión de usuarios.
    
    GET: Muestra el formulario de login
    POST: Procesa las credenciales y autentica al usuario
    
    Returns:
        Template de login o redirección según rol del usuario
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('contraseña', '')
            
            # Validar campos requeridos
            if not email or not password:
                flash('Email y contraseña son requeridos.', 'error')
                return render_template('login.html')
            
            # Buscar usuario
            user = Usuario.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.contraseña, password):
                login_user(user)
                logger.info(f"Login exitoso para usuario: {email} (rol: {user.rol})")
                
                # Redirigir según el rol del usuario
                if user.rol == 'cliente':
                    flash(f'¡Bienvenido/a {user.nombre}!', 'success')
                    return redirect(url_for('main.dashboard_cliente'))
                elif user.rol in ['admin', 'empleado']:
                    flash(f'¡Bienvenido/a {user.nombre}!', 'success')
                    return redirect(url_for('main.dashboard_admin'))
                else:
                    flash('¡Bienvenido/a!', 'success')
                    return redirect(url_for('main.home'))
            else:
                logger.warning(f"Intento de login fallido para email: {email}")
                flash('Email o contraseña incorrectos.', 'error')
                
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error interno del servidor. Intenta nuevamente.', 'error')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """
    Controlador para cerrar sesión del usuario actual.
    
    Returns:
        Redirección a la página de login
    """
    try:
        user_email = current_user.email if current_user.is_authenticated else 'Desconocido'
        logout_user()
        logger.info(f"Logout exitoso para usuario: {user_email}")
        flash('Sesión cerrada exitosamente.', 'info')
        return redirect(url_for('main.login'))
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Controlador para el registro de nuevos usuarios.
    
    GET: Muestra el formulario de registro
    POST: Procesa los datos del usuario y crea una nueva cuenta
    
    Returns:
        Template de registro o redirección a login si es exitoso
    """
    if request.method == 'POST':
        try:
            from app.utils import validar_email, validar_password, sanitizar_texto, validar_campos_requeridos
            
            # Obtener y sanitizar datos del formulario
            nombre = sanitizar_texto(request.form.get('nombre', ''))
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('contraseña', '')
            rol = request.form.get('rol', 'cliente')
            
            # Validar campos requeridos
            errores = validar_campos_requeridos(
                {'nombre': nombre, 'email': email, 'contraseña': password},
                ['nombre', 'email', 'contraseña']
            )
            
            # Validar email
            if email and not validar_email(email):
                errores.append('El formato del email no es válido')
            
            # Validar contraseña
            if password:
                errores_password = validar_password(password)
                errores.extend(errores_password)
            
            # Validar longitud del nombre
            if len(nombre) < 2:
                errores.append('El nombre debe tener al menos 2 caracteres')
            elif len(nombre) > 100:
                errores.append('El nombre no puede exceder 100 caracteres')
            
            # Validar rol
            if rol not in ['admin', 'empleado', 'cliente']:
                errores.append('Rol inválido')
            
            # Mostrar errores si los hay
            if errores:
                for error in errores:
                    flash(error, 'error')
                logger.warning(f"Errores de validación en registro para email: {email}")
                return render_template('register.html')
            
            # Verificar si el email ya existe
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                flash('El correo ya está registrado.', 'error')
                logger.warning(f"Intento de registro con email duplicado: {email}")
                return render_template('register.html')

            # Crear el usuario usando el servicio si está disponible
            if UsuarioService:
                resultado = UsuarioService.crear_usuario(nombre, email, password, rol)
                if resultado['success']:
                    logger.info(f"Usuario registrado exitosamente: {email} (rol: {rol})")
                    flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                    return redirect(url_for('main.login'))
                else:
                    flash(resultado['message'], 'error')
                    return render_template('register.html')
            else:
                # Fallback: crear usuario directamente
                nuevo_usuario = Usuario(
                    nombre=nombre,
                    email=email,
                    contraseña=generate_password_hash(password),
                    rol=rol
                )
                db.session.add(nuevo_usuario)
                db.session.commit()
                logger.info(f"Usuario registrado exitosamente (fallback): {email} (rol: {rol})")
                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('main.login'))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {str(e)}")
            flash('Error interno del servidor. Intenta nuevamente.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

# =============================================================================
# RUTAS DE GESTIÓN DE HABITACIONES
# =============================================================================

@main.route('/habitaciones')
@login_required
@admin_or_empleado_required
def listar_habitaciones():
    """
    Controlador para listar todas las habitaciones.
    Requiere permisos de administrador o empleado.
    
    Returns:
        Template con la lista de habitaciones
    """
    try:
        habitaciones = Habitacion.query.all()
        logger.info(f"Listado de habitaciones solicitado por {current_user.email}")
        return render_template('habitaciones/listar.html', habitaciones=habitaciones)
    except Exception as e:
        logger.error(f"Error al listar habitaciones: {str(e)}")
        flash('Error al cargar las habitaciones.', 'error')
        return render_template('habitaciones/listar.html', habitaciones=[])

@main.route('/habitaciones/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_habitacion():
    """
    Controlador para crear una nueva habitación.
    Requiere permisos de administrador.
    
    GET: Muestra el formulario de creación
    POST: Procesa los datos y crea la habitación
    
    Returns:
        Template del formulario o redirección a lista si es exitoso
    """
    try:
        tipos = TipoHabitacion.query.all()
        
        if request.method == 'POST':
            # Obtener y validar datos del formulario
            numero = request.form.get('numero', '').strip()
            tipo = request.form.get('tipo', '').strip()
            precio = request.form.get('precio', '')
            descripcion = request.form.get('descripcion', '').strip()
            disponible = 'disponible' in request.form
            tipo_id = request.form.get('tipo_id', '')
            
            # Validaciones básicas
            errores = []
            if not numero:
                errores.append('El número de habitación es requerido')
            elif len(numero) > 10:
                errores.append('El número de habitación no puede exceder 10 caracteres')
            
            if not tipo:
                errores.append('El tipo de habitación es requerido')
            
            # Validar precio
            try:
                precio_float = float(precio)
                if precio_float <= 0:
                    errores.append('El precio debe ser mayor a cero')
                elif precio_float > 10000:
                    errores.append('El precio parece demasiado alto')
            except (ValueError, TypeError):
                errores.append('El precio debe ser un número válido')
            
            if not tipo_id:
                errores.append('Debe seleccionar un tipo de habitación')
            
            # Verificar que el número no esté duplicado
            habitacion_existente = Habitacion.query.filter_by(numero=numero).first()
            if habitacion_existente:
                errores.append('Ya existe una habitación con ese número')
            
            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('habitaciones/nueva.html', tipos=tipos)
            
            # Crear habitación
            habitacion = Habitacion(
                numero=numero,
                tipo=tipo,
                precio=precio_float,
                descripcion=descripcion,
                disponible=disponible,
                tipo_id=tipo_id
            )
            db.session.add(habitacion)
            db.session.commit()
            
            logger.info(f"Habitación {numero} creada por {current_user.email}")
            flash('Habitación creada exitosamente.', 'success')
            return redirect(url_for('main.listar_habitaciones'))
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear habitación: {str(e)}")
        flash('Error al crear la habitación. Intenta nuevamente.', 'error')
        
    return render_template('habitaciones/nueva.html', tipos=tipos)

@main.route('/habitaciones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_habitacion(id):
    """
    Controlador para editar una habitación existente.
    Requiere permisos de administrador.
    
    Args:
        id: ID de la habitación a editar
        
    GET: Muestra el formulario pre-poblado
    POST: Procesa los cambios y actualiza la habitación
    
    Returns:
        Template del formulario o redirección a lista si es exitoso
    """
    try:
        habitacion = Habitacion.query.get_or_404(id)
        tipos = TipoHabitacion.query.all()
        
        if request.method == 'POST':
            # Obtener datos del formulario
            numero = request.form.get('numero', '').strip()
            tipo = request.form.get('tipo', '').strip()
            precio = request.form.get('precio', '')
            descripcion = request.form.get('descripcion', '').strip()
            disponible = 'disponible' in request.form
            tipo_id = request.form.get('tipo_id', '')
            
            # Validaciones
            errores = []
            if not numero:
                errores.append('El número de habitación es requerido')
            
            # Verificar número duplicado (excluyendo la habitación actual)
            habitacion_existente = Habitacion.query.filter(
                Habitacion.numero == numero,
                Habitacion.id != id
            ).first()
            if habitacion_existente:
                errores.append('Ya existe otra habitación con ese número')
            
            # Validar precio
            try:
                precio_float = float(precio)
                if precio_float <= 0:
                    errores.append('El precio debe ser mayor a cero')
            except (ValueError, TypeError):
                errores.append('El precio debe ser un número válido')
            
            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('habitaciones/editar.html', habitacion=habitacion, tipos=tipos)
            
            # Actualizar habitación
            habitacion.numero = numero
            habitacion.tipo = tipo
            habitacion.precio = precio_float
            habitacion.descripcion = descripcion
            habitacion.disponible = disponible
            habitacion.tipo_id = tipo_id
            
            db.session.commit()
            logger.info(f"Habitación {habitacion.numero} editada por {current_user.email}")
            flash('Habitación actualizada exitosamente.', 'success')
            return redirect(url_for('main.listar_habitaciones'))
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al editar habitación {id}: {str(e)}")
        flash('Error al actualizar la habitación.', 'error')
        
    return render_template('habitaciones/editar.html', habitacion=habitacion, tipos=tipos)

@main.route('/habitaciones/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_habitacion(id):
    """
    Controlador para eliminar una habitación.
    Requiere permisos de administrador.
    
    Args:
        id: ID de la habitación a eliminar
        
    Returns:
        Redirección a la lista de habitaciones
    """
    try:
        habitacion = Habitacion.query.get_or_404(id)
        
        # Verificar si tiene reservas activas
        reservas_activas = Reserva.query.filter(
            Reserva.habitacion_id == id,
            Reserva.estado.in_(['pendiente', 'confirmada'])
        ).count()
        
        if reservas_activas > 0:
            flash('No se puede eliminar la habitación porque tiene reservas activas.', 'error')
            logger.warning(f"Intento de eliminar habitación {habitacion.numero} con reservas activas")
            return redirect(url_for('main.listar_habitaciones'))
        
        numero_habitacion = habitacion.numero
        db.session.delete(habitacion)
        db.session.commit()
        
        logger.info(f"Habitación {numero_habitacion} eliminada por {current_user.email}")
        flash('Habitación eliminada exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar habitación {id}: {str(e)}")
        flash('Error al eliminar la habitación.', 'error')
        
    return redirect(url_for('main.listar_habitaciones'))

# =============================================================================
# RUTAS DE GESTIÓN DE TIPOS DE HABITACIÓN
# =============================================================================

@main.route('/tipos_habitacion')
@login_required
@admin_or_empleado_required
def listar_tipos_habitacion():
    """
    Controlador para listar todos los tipos de habitación.
    Requiere permisos de administrador o empleado.
    
    Returns:
        Template con la lista de tipos de habitación
    """
    try:
        tipos = TipoHabitacion.query.all()
        logger.info(f"Listado de tipos de habitación solicitado por {current_user.email}")
        return render_template('tipos_habitacion/listar.html', tipos=tipos)
    except Exception as e:
        logger.error(f"Error al listar tipos de habitación: {str(e)}")
        flash('Error al cargar los tipos de habitación.', 'error')
        return render_template('tipos_habitacion/listar.html', tipos=[])

@main.route('/tipos_habitacion/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_tipo_habitacion():
    """
    Controlador para crear un nuevo tipo de habitación.
    Requiere permisos de administrador.
    
    GET: Muestra el formulario de creación
    POST: Procesa los datos y crea el tipo
    
    Returns:
        Template del formulario o redirección a lista si es exitoso
    """
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            
            # Validaciones
            errores = []
            if not nombre:
                errores.append('El nombre es requerido')
            elif len(nombre) < 2:
                errores.append('El nombre debe tener al menos 2 caracteres')
            elif len(nombre) > 50:
                errores.append('El nombre no puede exceder 50 caracteres')
            
            # Verificar que el nombre no esté duplicado
            tipo_existente = TipoHabitacion.query.filter_by(nombre=nombre).first()
            if tipo_existente:
                errores.append('Ya existe un tipo con ese nombre')
            
            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('tipos_habitacion/nuevo.html')
            
            # Crear tipo de habitación
            tipo = TipoHabitacion(nombre=nombre, descripcion=descripcion)
            db.session.add(tipo)
            db.session.commit()
            
            logger.info(f"Tipo de habitación '{nombre}' creado por {current_user.email}")
            flash('Tipo de habitación creado exitosamente.', 'success')
            return redirect(url_for('main.listar_tipos_habitacion'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear tipo de habitación: {str(e)}")
            flash('Error al crear el tipo de habitación.', 'error')
            
    return render_template('tipos_habitacion/nuevo.html')

@main.route('/tipos_habitacion/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tipo_habitacion(id):
    tipo = TipoHabitacion.query.get_or_404(id)
    if request.method == 'POST':
        tipo.nombre = request.form['nombre']
        tipo.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Tipo de habitación actualizado.')
        return redirect(url_for('main.listar_tipos_habitacion'))
    return render_template('tipos_habitacion/editar.html', tipo=tipo)

@main.route('/tipos_habitacion/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_tipo_habitacion(id):
    tipo = TipoHabitacion.query.get_or_404(id)
    db.session.delete(tipo)
    db.session.commit()
    flash('Tipo de habitación eliminado.')
    return redirect(url_for('main.listar_tipos_habitacion'))

@main.route('/servicios_extra')
@login_required
def listar_servicios_extra():
    servicios = ServicioExtra.query.all()
    return render_template('servicios_extra/listar.html', servicios=servicios)

@main.route('/servicios_extra/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio_extra():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        servicio = ServicioExtra(nombre=nombre, descripcion=descripcion, precio=precio)
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio extra creado exitosamente.')
        return redirect(url_for('main.listar_servicios_extra'))
    return render_template('servicios_extra/nuevo.html')

@main.route('/servicios_extra/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_servicio_extra(id):
    servicio = ServicioExtra.query.get_or_404(id)
    if request.method == 'POST':
        servicio.nombre = request.form['nombre']
        servicio.descripcion = request.form['descripcion']
        servicio.precio = request.form['precio']
        db.session.commit()
        flash('Servicio extra actualizado.')
        return redirect(url_for('main.listar_servicios_extra'))
    return render_template('servicios_extra/editar.html', servicio=servicio)

@main.route('/servicios_extra/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_servicio_extra(id):
    servicio = ServicioExtra.query.get_or_404(id)
    db.session.delete(servicio)
    db.session.commit()
    flash('Servicio extra eliminado.')
    return redirect(url_for('main.listar_servicios_extra'))

# =============================================================================
# RUTAS DE GESTIÓN DE RESERVAS
# =============================================================================

@main.route('/reservas')
@login_required
@admin_or_empleado_required
def listar_reservas():
    """
    Controlador para listar todas las reservas.
    Requiere permisos de administrador o empleado.
    
    Returns:
        Template con la lista de reservas
    """
    try:
        # Los clientes solo ven sus propias reservas
        if current_user.rol == 'cliente':
            reservas = Reserva.query.filter_by(usuario_id=current_user.id).all()
        else:
            reservas = Reserva.query.all()
            
        logger.info(f"Listado de reservas solicitado por {current_user.email}")
        return render_template('reservas/listar.html', reservas=reservas)
    except Exception as e:
        logger.error(f"Error al listar reservas: {str(e)}")
        flash('Error al cargar las reservas.', 'error')
        return render_template('reservas/listar.html', reservas=[])

@main.route('/reservas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_reserva():
    """
    Controlador para crear una nueva reserva.
    Los clientes pueden crear sus propias reservas.
    Los admin/empleados pueden crear reservas para cualquier usuario.
    
    GET: Muestra el formulario de creación
    POST: Procesa los datos y crea la reserva
    
    Returns:
        Template del formulario o redirección a lista si es exitoso
    """
    try:
        habitaciones = Habitacion.query.filter_by(disponible=True).all()
        servicios = ServicioExtra.query.all()
        
        # Los admin/empleados pueden crear reservas para cualquier usuario
        if current_user.rol in ['admin', 'empleado']:
            usuarios = Usuario.query.filter_by(rol='cliente').all()
        else:
            usuarios = [current_user]  # Los clientes solo pueden reservar para sí mismos
        
        if request.method == 'POST':
            # Obtener datos del formulario
            usuario_id = request.form.get('usuario_id') if current_user.rol in ['admin', 'empleado'] else current_user.id
            habitacion_id = request.form.get('habitacion_id')
            fecha_inicio_str = request.form.get('fecha_inicio')
            fecha_fin_str = request.form.get('fecha_fin')
            estado = request.form.get('estado', 'pendiente')
            servicios_ids = request.form.getlist('servicios')
            
            # Usar el servicio de reservas si está disponible
            if ReservaService:
                resultado = ReservaService.crear_reserva(
                    usuario_id=usuario_id,
                    habitacion_id=habitacion_id,
                    fecha_inicio=fecha_inicio_str,
                    fecha_fin=fecha_fin_str,
                    estado=estado,
                    servicios_ids=servicios_ids
                )
                
                if resultado['success']:
                    logger.info(f"Reserva creada por {current_user.email} para usuario {usuario_id}")
                    flash('Reserva creada exitosamente.', 'success')
                    return redirect(url_for('main.listar_reservas'))
                else:
                    flash(resultado['message'], 'error')
                    return render_template('reservas/nueva.html', 
                                         habitaciones=habitaciones, 
                                         usuarios=usuarios, 
                                         servicios=servicios, 
                                         today=date.today())
            else:
                # Fallback: lógica de validación directa
                errores = []
                
                # Validar campos requeridos
                if not all([usuario_id, habitacion_id, fecha_inicio_str, fecha_fin_str]):
                    errores.append('Todos los campos obligatorios deben ser completados')
                
                if errores:
                    for error in errores:
                        flash(error, 'error')
                    return render_template('reservas/nueva.html', 
                                         habitaciones=habitaciones, 
                                         usuarios=usuarios, 
                                         servicios=servicios, 
                                         today=date.today())
                
                try:
                    # Convertir y validar fechas
                    from app.utils import validar_fechas_reserva
                    errores_fechas = validar_fechas_reserva(fecha_inicio_str, fecha_fin_str)
                    
                    if errores_fechas:
                        for error in errores_fechas:
                            flash(error, 'error')
                        return render_template('reservas/nueva.html', 
                                             habitaciones=habitaciones, 
                                             usuarios=usuarios, 
                                             servicios=servicios, 
                                             today=date.today())
                    
                    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                    
                    # Verificar disponibilidad de habitación
                    conflictos = Reserva.query.filter(
                        Reserva.habitacion_id == habitacion_id,
                        Reserva.estado.in_(['pendiente', 'confirmada']),
                        Reserva.fecha_inicio < fecha_fin,
                        Reserva.fecha_fin > fecha_inicio
                    ).first()
                    
                    if conflictos:
                        flash('La habitación no está disponible en las fechas seleccionadas.', 'error')
                        return render_template('reservas/nueva.html', 
                                             habitaciones=habitaciones, 
                                             usuarios=usuarios, 
                                             servicios=servicios, 
                                             today=date.today())
                    
                    # Crear reserva
                    reserva = Reserva(
                        usuario_id=usuario_id,
                        habitacion_id=habitacion_id,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        estado=estado
                    )
                    db.session.add(reserva)
                    db.session.commit()
                    
                    # Relacionar servicios extra
                    for sid in servicios_ids:
                        if sid:
                            servicio = ServicioExtra.query.get(int(sid))
                            if servicio:
                                reserva.servicios.append(servicio)
                    
                    db.session.commit()
                    logger.info(f"Reserva creada (fallback) por {current_user.email}")
                    flash('Reserva creada exitosamente.', 'success')
                    return redirect(url_for('main.listar_reservas'))
                    
                except ValueError as e:
                    flash('Formato de fecha inválido.', 'error')
                    logger.warning(f"Error de formato de fecha en reserva: {str(e)}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error al crear reserva: {str(e)}")
                    flash('Error interno del servidor. Intenta nuevamente.', 'error')
        
        # Para GET request
        return render_template('reservas/nueva.html', 
                             habitaciones=habitaciones, 
                             usuarios=usuarios, 
                             servicios=servicios, 
                             today=date.today())
                             
    except Exception as e:
        logger.error(f"Error en nueva_reserva: {str(e)}")
        flash('Error al cargar el formulario de reserva.', 'error')
        return redirect(url_for('main.listar_reservas'))

@main.route('/reservas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    habitaciones = Habitacion.query.all()
    usuarios = Usuario.query.all()
    servicios = ServicioExtra.query.all()
    if request.method == 'POST':
        reserva.usuario_id = request.form['usuario_id']
        reserva.habitacion_id = request.form['habitacion_id']
        reserva.fecha_inicio = request.form['fecha_inicio']
        reserva.fecha_fin = request.form['fecha_fin']
        reserva.estado = request.form['estado']
        # Actualizar servicios extra
        reserva.servicios.clear()
        servicios_ids = request.form.getlist('servicios')
        for sid in servicios_ids:
            servicio = ServicioExtra.query.get(int(sid))
            reserva.servicios.append(servicio)
        db.session.commit()
        flash('Reserva actualizada.')
        return redirect(url_for('main.listar_reservas'))
    return render_template('reservas/editar.html', reserva=reserva, habitaciones=habitaciones, usuarios=usuarios, servicios=servicios)

@main.route('/reservas/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    flash('Reserva eliminada.')
    return redirect(url_for('main.listar_reservas'))

# =============================================================================
# RUTAS DE GESTIÓN DE PROMOCIONES
# =============================================================================

@main.route('/promociones')
@login_required
@admin_or_empleado_required
def listar_promociones():
    """
    Controlador para listar todas las promociones.
    Requiere permisos de administrador o empleado.
    
    Returns:
        Template con la lista de promociones y estadísticas
    """
    try:
        # Usar servicio para obtener promociones con estado calculado
        if PromocionService:
            promociones_con_estado = PromocionService.obtener_promociones_con_estado()
            estadisticas = PromocionService.obtener_estadisticas_promociones()
        else:
            # Fallback: obtener promociones básicas
            promociones = Promocion.query.all()
            promociones_con_estado = [{'promocion': p, 'estado': 'N/A', 'activa': False} for p in promociones]
            estadisticas = {'total': len(promociones), 'activas': 0}
        
        logger.info(f"Listado de promociones solicitado por {current_user.email}")
        return render_template('promociones/listar.html', 
                             promociones_data=promociones_con_estado,
                             estadisticas=estadisticas)
    except Exception as e:
        logger.error(f"Error al listar promociones: {str(e)}")
        flash('Error al cargar las promociones.', 'error')
        return render_template('promociones/listar.html', 
                             promociones_data=[], 
                             estadisticas={'total': 0})

@main.route('/promociones/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_promocion():
    """
    Controlador para crear una nueva promoción.
    Requiere permisos de administrador.
    
    GET: Muestra el formulario de creación
    POST: Procesa los datos y crea la promoción
    
    Returns:
        Template del formulario o redirección a lista si es exitoso
    """
    if request.method == 'POST':
        try:
            descripcion = request.form.get('descripcion', '').strip()
            descuento = request.form.get('descuento', '')
            fecha_inicio = request.form.get('fecha_inicio', '')
            fecha_fin = request.form.get('fecha_fin', '')
            
            # Usar servicio para crear promoción si está disponible
            if PromocionService:
                resultado = PromocionService.crear_promocion(descripcion, descuento, fecha_inicio, fecha_fin)
                
                if resultado['success']:
                    logger.info(f"Promoción '{descripcion[:30]}...' creada por {current_user.email}")
                    flash('Promoción creada exitosamente.', 'success')
                    return redirect(url_for('main.listar_promociones'))
                else:
                    flash(resultado['message'], 'error')
                    return render_template('promociones/nueva.html')
            else:
                # Fallback: lógica directa
                from app.utils import validar_campos_requeridos
                
                errores = validar_campos_requeridos(
                    {'descripcion': descripcion, 'descuento': descuento, 
                     'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin},
                    ['descripcion', 'descuento', 'fecha_inicio', 'fecha_fin']
                )
                
                if errores:
                    for error in errores:
                        flash(error, 'error')
                    return render_template('promociones/nueva.html')
                
                # Crear promoción directamente
                promocion = Promocion(
                    descripcion=descripcion,
                    descuento=float(descuento),
                    fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
                    fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                )
                db.session.add(promocion)
                db.session.commit()
                
                logger.info(f"Promoción '{descripcion[:30]}...' creada (fallback) por {current_user.email}")
                flash('Promoción creada exitosamente.', 'success')
                return redirect(url_for('main.listar_promociones'))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear promoción: {str(e)}")
            flash('Error al crear la promoción. Intenta nuevamente.', 'error')
            
    return render_template('promociones/nueva.html')

@main.route('/promociones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_promocion(id):
    promocion = Promocion.query.get_or_404(id)
    if request.method == 'POST':
        promocion.descripcion = request.form['descripcion']
        promocion.descuento = request.form['descuento']
        promocion.fecha_inicio = request.form['fecha_inicio']
        promocion.fecha_fin = request.form['fecha_fin']
        db.session.commit()
        flash('Promoción actualizada.')
        return redirect(url_for('main.listar_promociones'))
    return render_template('promociones/editar.html', promocion=promocion)

@main.route('/promociones/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_promocion(id):
    promocion = Promocion.query.get_or_404(id)
    db.session.delete(promocion)
    db.session.commit()
    flash('Promoción eliminada.')
    return redirect(url_for('main.listar_promociones'))

from app.models import Opinion, Habitacion
from app import db

@main.route('/opiniones')
@login_required
def listar_opiniones():
    opiniones = Opinion.query.all()
    return render_template('opiniones/listar.html', opiniones=opiniones)

@main.route('/opiniones/nueva', methods=['GET', 'POST'])
@login_required
def nueva_opinion():
    habitaciones = Habitacion.query.all()
    if request.method == 'POST':
        habitacion_id = request.form['habitacion_id']
        comentario = request.form['comentario']
        calificacion = request.form['calificacion']
        opinion = Opinion(
            usuario_id=current_user.id,
            habitacion_id=habitacion_id,
            comentario=comentario,
            calificacion=calificacion,
            fecha=datetime.utcnow()
        )
        db.session.add(opinion)
        db.session.commit()
        flash('¡Gracias por tu opinión!')
        return redirect(url_for('main.listar_opiniones'))
    return render_template('opiniones/nueva.html', habitaciones=habitaciones)

@main.route('/opiniones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    if opinion.usuario_id != current_user.id:
        flash('No puedes editar opiniones de otros usuarios.')
        return redirect(url_for('main.listar_opiniones'))
    habitaciones = Habitacion.query.all()
    if request.method == 'POST':
        opinion.habitacion_id = request.form['habitacion_id']
        opinion.comentario = request.form['comentario']
        opinion.calificacion = request.form['calificacion']
        db.session.commit()
        flash('Opinión actualizada.')
        return redirect(url_for('main.listar_opiniones'))
    return render_template('opiniones/editar.html', opinion=opinion, habitaciones=habitaciones)

@main.route('/opiniones/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    if opinion.usuario_id != current_user.id:
        flash('No puedes eliminar opiniones de otros usuarios.')
        return redirect(url_for('main.listar_opiniones'))
    db.session.delete(opinion)
    db.session.commit()
    flash('Opinión eliminada.')
    return redirect(url_for('main.listar_opiniones'))

@main.route('/dashboard/cliente')
@login_required
def dashboard_cliente():
    """Dashboard personalizado para clientes"""
    if current_user.rol != 'cliente':
        flash('Acceso denegado.')
        return redirect(url_for('main.home'))
    
    # Obtener todas las habitaciones disponibles
    habitaciones = Habitacion.query.filter_by(disponible=True).all()
    
    # Obtener reservas del cliente actual
    reservas_usuario = Reserva.query.filter_by(usuario_id=current_user.id).order_by(Reserva.fecha_inicio.desc()).limit(5).all()
    
    # Obtener servicios extra disponibles
    servicios_extra = ServicioExtra.query.all()
    
    # Obtener promociones activas
    from datetime import date
    promociones_activas = Promocion.query.filter(
        Promocion.fecha_inicio <= date.today(),
        Promocion.fecha_fin >= date.today()
    ).all()
    
    # Obtener tipos de habitación para filtros
    tipos_habitacion = TipoHabitacion.query.all()
    
    return render_template('dashboard/cliente.html', 
                         habitaciones=habitaciones,
                         reservas=reservas_usuario,
                         servicios=servicios_extra,
                         promociones=promociones_activas,
                         tipos=tipos_habitacion,
                         usuario=current_user)

@main.route('/habitacion/<int:habitacion_id>')
@login_required
def detalle_habitacion(habitacion_id):
    """Página dedicada para una habitación específica"""
    # Verificar que es cliente
    if current_user.rol != 'cliente':
        flash('Acceso denegado.')
        return redirect(url_for('main.home'))
    
    # Obtener la habitación o retornar 404
    habitacion = Habitacion.query.get_or_404(habitacion_id)
    
    # Obtener habitaciones similares para comparación (mismo tipo, excluyendo la actual)
    habitaciones_similares = Habitacion.query.filter(
        Habitacion.tipo_id == habitacion.tipo_id,
        Habitacion.id != habitacion.id,
        Habitacion.disponible == True
    ).limit(3).all()
    
    # Obtener todas las habitaciones disponibles para comparar
    todas_habitaciones = Habitacion.query.filter(
        Habitacion.id != habitacion.id,
        Habitacion.disponible == True
    ).all()
    
    # Obtener servicios extra disponibles
    servicios_extra = ServicioExtra.query.all()
    
    # Obtener promociones activas
    from datetime import date
    promociones_activas = Promocion.query.filter(
        Promocion.fecha_inicio <= date.today(),
        Promocion.fecha_fin >= date.today()
    ).all()
    
    # Obtener opiniones de esta habitación (si tienes un modelo de opiniones por habitación)
    # opiniones = Opinion.query.filter_by(habitacion_id=habitacion_id).order_by(Opinion.fecha.desc()).limit(5).all()
    
    return render_template('habitacion/detalle.html',
                         habitacion=habitacion,
                         habitaciones_similares=habitaciones_similares,
                         todas_habitaciones=todas_habitaciones,
                         servicios=servicios_extra,
                         promociones=promociones_activas,
                         usuario=current_user)

@main.route('/dashboard/admin')
@login_required
def dashboard_admin():
    """Dashboard para administradores y empleados"""
    if current_user.rol not in ['admin', 'empleado']:
        flash('Acceso denegado.')
        return redirect(url_for('main.home'))
    
    # Obtener estadísticas para el dashboard
    total_habitaciones = Habitacion.query.count()
    habitaciones_disponibles = Habitacion.query.filter_by(disponible=True).count()
    total_reservas = Reserva.query.count()
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
    reservas_confirmadas = Reserva.query.filter_by(estado='confirmada').count()
    total_usuarios = Usuario.query.filter_by(rol='cliente').count()
    total_promociones = Promocion.query.count()
    total_servicios = ServicioExtra.query.count()
    
    # Reservas recientes (últimas 5)
    reservas_recientes = Reserva.query.order_by(Reserva.id.desc()).limit(5).all()
    
    # Calcular ingresos totales (estimado)
    ingresos_estimados = 0
    for reserva in Reserva.query.filter_by(estado='confirmada').all():
        dias = (reserva.fecha_fin - reserva.fecha_inicio).days
        ingresos_estimados += reserva.habitacion.precio * dias
    
    return render_template('dashboard/admin.html', 
                         usuario=current_user,
                         stats={
                             'total_habitaciones': total_habitaciones,
                             'habitaciones_disponibles': habitaciones_disponibles,
                             'total_reservas': total_reservas,
                             'reservas_pendientes': reservas_pendientes,
                             'reservas_confirmadas': reservas_confirmadas,
                             'total_usuarios': total_usuarios,
                             'total_promociones': total_promociones,
                             'total_servicios': total_servicios,
                             'ingresos_estimados': ingresos_estimados
                         },
                         reservas_recientes=reservas_recientes)

@main.route('/debug-sidebar')
def debug_sidebar():
    """Página de depuración del sidebar"""
    return render_template('test_sidebar_debug.html')