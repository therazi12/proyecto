"""
Servicios de Negocio para el Sistema Hotelero - Hotel Paraíso Real
================================================================

Este módulo contiene la lógica de negocio del sistema, implementando
el patrón Service Layer para separar la lógica de negocio de los controladores.

Autor: [Tu nombre]
Fecha: Junio 2025
Versión: 1.0
"""

from app.models import Usuario, Habitacion, Reserva, ServicioExtra, Promocion, Opinion, TipoHabitacion
from app import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class UsuarioService:
    """
    Servicio para gestionar operaciones relacionadas con usuarios.
    """
    
    @staticmethod
    def crear_usuario(nombre, email, password, rol='cliente'):
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            nombre (str): Nombre completo del usuario
            email (str): Email único del usuario
            password (str): Contraseña en texto plano
            rol (str): Rol del usuario (admin, empleado, cliente)
            
        Returns:
            tuple: (Usuario, bool) - Usuario creado y éxito de la operación
        """
        try:
            # Verificar si el email ya existe
            if Usuario.query.filter_by(email=email).first():
                logger.warning(f"Intento de crear usuario con email duplicado: {email}")
                return None, False
            
            # Crear nuevo usuario
            usuario = Usuario(
                nombre=nombre,
                email=email,
                rol=rol
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            logger.info(f"Usuario creado exitosamente: {email} con rol {rol}")
            return usuario, True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear usuario {email}: {str(e)}")
            return None, False
    
    @staticmethod
    def autenticar_usuario(email, password):
        """
        Autentica a un usuario con email y contraseña.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            Usuario: Usuario autenticado o None si falla
        """
        try:
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and usuario.check_password(password):
                logger.info(f"Usuario autenticado exitosamente: {email}")
                return usuario
            
            logger.warning(f"Intento de autenticación fallido para: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error en autenticación para {email}: {str(e)}")
            return None


class ReservaService:
    """
    Servicio para gestionar operaciones relacionadas con reservas.
    """
    
    @staticmethod
    def crear_reserva(usuario_id, habitacion_id, fecha_inicio, fecha_fin, servicios_ids=None):
        """
        Crea una nueva reserva verificando disponibilidad.
        
        Args:
            usuario_id (int): ID del usuario
            habitacion_id (int): ID de la habitación
            fecha_inicio (date): Fecha de check-in
            fecha_fin (date): Fecha de check-out
            servicios_ids (list): Lista de IDs de servicios extra
            
        Returns:
            tuple: (Reserva, bool, str) - Reserva creada, éxito y mensaje
        """
        try:
            # Verificar disponibilidad de la habitación
            if not ReservaService.verificar_disponibilidad(habitacion_id, fecha_inicio, fecha_fin):
                return None, False, "La habitación no está disponible en las fechas seleccionadas"
            
            # Verificar que las fechas sean válidas
            if fecha_inicio >= fecha_fin:
                return None, False, "La fecha de fin debe ser posterior a la fecha de inicio"
            
            if fecha_inicio < date.today():
                return None, False, "No se pueden hacer reservas en fechas pasadas"
            
            # Crear la reserva
            reserva = Reserva(
                usuario_id=usuario_id,
                habitacion_id=habitacion_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='pendiente'
            )
            
            # Agregar servicios extra si se proporcionaron
            if servicios_ids:
                servicios = ServicioExtra.query.filter(ServicioExtra.id.in_(servicios_ids)).all()
                reserva.servicios.extend(servicios)
            
            db.session.add(reserva)
            db.session.commit()
            
            logger.info(f"Reserva creada exitosamente: ID {reserva.id}")
            return reserva, True, "Reserva creada exitosamente"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear reserva: {str(e)}")
            return None, False, f"Error al crear la reserva: {str(e)}"
    
    @staticmethod
    def verificar_disponibilidad(habitacion_id, fecha_inicio, fecha_fin):
        """
        Verifica si una habitación está disponible en el rango de fechas.
        
        Args:
            habitacion_id (int): ID de la habitación
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        try:
            # Buscar reservas que se solapen con las fechas solicitadas
            reservas_solapadas = Reserva.query.filter(
                Reserva.habitacion_id == habitacion_id,
                Reserva.estado.in_(['confirmada', 'pendiente']),
                db.or_(
                    db.and_(Reserva.fecha_inicio <= fecha_inicio, Reserva.fecha_fin > fecha_inicio),
                    db.and_(Reserva.fecha_inicio < fecha_fin, Reserva.fecha_fin >= fecha_fin),
                    db.and_(Reserva.fecha_inicio >= fecha_inicio, Reserva.fecha_fin <= fecha_fin)
                )
            ).first()
            
            return reservas_solapadas is None
            
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {str(e)}")
            return False
    
    @staticmethod
    def calcular_total_reserva(habitacion_id, fecha_inicio, fecha_fin, servicios_ids=None):
        """
        Calcula el total de una reserva incluyendo servicios extra.
        
        Args:
            habitacion_id (int): ID de la habitación
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            servicios_ids (list): Lista de IDs de servicios extra
            
        Returns:
            dict: Desglose del costo total
        """
        try:
            habitacion = Habitacion.query.get(habitacion_id)
            if not habitacion:
                return {'error': 'Habitación no encontrada'}
            
            # Calcular noches
            noches = (fecha_fin - fecha_inicio).days
            
            # Costo de habitación
            costo_habitacion = habitacion.precio * noches
            
            # Costo de servicios extra
            costo_servicios = 0
            servicios_detalle = []
            
            if servicios_ids:
                servicios = ServicioExtra.query.filter(ServicioExtra.id.in_(servicios_ids)).all()
                for servicio in servicios:
                    costo_servicios += servicio.precio
                    servicios_detalle.append({
                        'nombre': servicio.nombre,
                        'precio': servicio.precio
                    })
            
            total = costo_habitacion + costo_servicios
            
            return {
                'habitacion': habitacion.numero,
                'noches': noches,
                'costo_habitacion': costo_habitacion,
                'costo_servicios': costo_servicios,
                'servicios_detalle': servicios_detalle,
                'total': total
            }
            
        except Exception as e:
            logger.error(f"Error al calcular total de reserva: {str(e)}")
            return {'error': str(e)}


class EstadisticasService:
    """
    Servicio para generar estadísticas del sistema.
    """
    
    @staticmethod
    def obtener_estadisticas_dashboard():
        """
        Obtiene estadísticas generales para el dashboard.
        
        Returns:
            dict: Diccionario con estadísticas del sistema
        """
        try:
            # Estadísticas de usuarios
            total_usuarios = Usuario.query.count()
            usuarios_clientes = Usuario.query.filter_by(rol='cliente').count()
            
            # Estadísticas de habitaciones
            total_habitaciones = Habitacion.query.count()
            habitaciones_disponibles = Habitacion.query.filter_by(disponible=True).count()
            
            # Estadísticas de reservas
            total_reservas = Reserva.query.count()
            reservas_activas = Reserva.query.filter_by(estado='confirmada').count()
            reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
            
            # Estadísticas de ingresos (este mes)
            from sqlalchemy import func, extract
            mes_actual = datetime.now().month
            año_actual = datetime.now().year
            
            ingresos_mes = db.session.query(func.sum(
                Habitacion.precio * func.datediff(Reserva.fecha_fin, Reserva.fecha_inicio)
            )).join(Reserva).filter(
                extract('month', Reserva.fecha_reserva) == mes_actual,
                extract('year', Reserva.fecha_reserva) == año_actual,
                Reserva.estado == 'confirmada'
            ).scalar() or 0
            
            # Promociones activas
            promociones_activas = Promocion.query.filter(
                Promocion.fecha_inicio <= date.today(),
                Promocion.fecha_fin >= date.today(),
                Promocion.activa == True
            ).count()
            
            return {
                'usuarios': {
                    'total': total_usuarios,
                    'clientes': usuarios_clientes
                },
                'habitaciones': {
                    'total': total_habitaciones,
                    'disponibles': habitaciones_disponibles,
                    'ocupadas': total_habitaciones - habitaciones_disponibles
                },
                'reservas': {
                    'total': total_reservas,
                    'activas': reservas_activas,
                    'pendientes': reservas_pendientes
                },
                'ingresos': {
                    'mes_actual': float(ingresos_mes)
                },
                'promociones_activas': promociones_activas
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del dashboard: {str(e)}")
            return {}
    
    @staticmethod
    def obtener_ocupacion_por_tipo():
        """
        Obtiene estadísticas de ocupación por tipo de habitación.
        
        Returns:
            list: Lista con estadísticas por tipo de habitación
        """
        try:
            tipos = TipoHabitacion.query.all()
            estadisticas = []
            
            for tipo in tipos:
                total_habitaciones = tipo.habitaciones.count()
                habitaciones_ocupadas = sum(1 for hab in tipo.habitaciones if hab.esta_ocupada)
                
                porcentaje_ocupacion = (habitaciones_ocupadas / total_habitaciones * 100) if total_habitaciones > 0 else 0
                
                estadisticas.append({
                    'tipo': tipo.nombre,
                    'total_habitaciones': total_habitaciones,
                    'ocupadas': habitaciones_ocupadas,
                    'disponibles': total_habitaciones - habitaciones_ocupadas,
                    'porcentaje_ocupacion': round(porcentaje_ocupacion, 1)
                })
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error al obtener ocupación por tipo: {str(e)}")
            return []


class ValidacionService:
    """
    Servicio para validaciones de negocio.
    """
    
    @staticmethod
    def validar_datos_reserva(data):
        """
        Valida los datos de una reserva.
        
        Args:
            data (dict): Datos de la reserva
            
        Returns:
            tuple: (bool, list) - Válido y lista de errores
        """
        errores = []
        
        # Validar fechas
        try:
            fecha_inicio = datetime.strptime(data.get('fecha_inicio', ''), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(data.get('fecha_fin', ''), '%Y-%m-%d').date()
            
            if fecha_inicio >= fecha_fin:
                errores.append("La fecha de fin debe ser posterior a la fecha de inicio")
            
            if fecha_inicio < date.today():
                errores.append("No se pueden hacer reservas en fechas pasadas")
                
        except (ValueError, TypeError):
            errores.append("Formato de fecha inválido")
        
        # Validar usuario
        usuario_id = data.get('usuario_id')
        if not usuario_id or not Usuario.query.get(usuario_id):
            errores.append("Usuario no válido")
        
        # Validar habitación
        habitacion_id = data.get('habitacion_id')
        if not habitacion_id or not Habitacion.query.get(habitacion_id):
            errores.append("Habitación no válida")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_datos_usuario(data, es_edicion=False, usuario_id=None):
        """
        Valida los datos de un usuario.
        
        Args:
            data (dict): Datos del usuario
            es_edicion (bool): Si es una edición de usuario existente
            usuario_id (int): ID del usuario en caso de edición
            
        Returns:
            tuple: (bool, list) - Válido y lista de errores
        """
        errores = []
        
        # Validar email
        email = data.get('email', '').strip()
        if not email:
            errores.append("El email es obligatorio")
        elif '@' not in email or '.' not in email.split('@')[-1]:
            errores.append("Formato de email inválido")
        else:
            # Verificar email único
            query = Usuario.query.filter_by(email=email)
            if es_edicion and usuario_id:
                query = query.filter(Usuario.id != usuario_id)
            
            if query.first():
                errores.append("El email ya está en uso")
        
        # Validar nombre
        nombre = data.get('nombre', '').strip()
        if not nombre:
            errores.append("El nombre es obligatorio")
        elif len(nombre) < 2:
            errores.append("El nombre debe tener al menos 2 caracteres")
        
        # Validar contraseña (solo en creación o si se proporciona)
        password = data.get('password', '')
        if not es_edicion and not password:
            errores.append("La contraseña es obligatoria")
        elif password and len(password) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres")
        
        # Validar rol
        rol = data.get('rol', '')
        if rol not in ['admin', 'empleado', 'cliente']:
            errores.append("Rol no válido")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_promocion(descripcion, descuento, fecha_inicio, fecha_fin):
        """
        Valida los datos de una promoción.
        
        Args:
            descripcion: Descripción de la promoción
            descuento: Porcentaje de descuento
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            list: Lista de errores de validación
        """
        errores = []
        
        try:
            # Validar descripción
            if not descripcion or not descripcion.strip():
                errores.append('La descripción es requerida')
            elif len(descripcion.strip()) < 5:
                errores.append('La descripción debe tener al menos 5 caracteres')
            elif len(descripcion.strip()) > 200:
                errores.append('La descripción no puede exceder 200 caracteres')
            
            # Validar descuento
            try:
                descuento_float = float(descuento)
                if descuento_float <= 0:
                    errores.append('El descuento debe ser mayor a 0')
                elif descuento_float > 100:
                    errores.append('El descuento no puede ser mayor a 100%')
                elif descuento_float > 80:
                    errores.append('Descuentos superiores al 80% requieren aprobación especial')
            except (ValueError, TypeError):
                errores.append('El descuento debe ser un número válido')
            
            # Validar fechas
            from datetime import datetime, date
            
            try:
                if isinstance(fecha_inicio, str):
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                if isinstance(fecha_fin, str):
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                
                hoy = date.today()
                
                if fecha_inicio < hoy:
                    errores.append('La fecha de inicio no puede ser anterior a hoy')
                
                if fecha_fin <= fecha_inicio:
                    errores.append('La fecha de fin debe ser posterior a la fecha de inicio')
                
                # Validar duración de la promoción
                duracion = (fecha_fin - fecha_inicio).days
                if duracion > 365:
                    errores.append('La promoción no puede durar más de un año')
                elif duracion < 1:
                    errores.append('La promoción debe durar al menos un día')
                
            except ValueError:
                errores.append('Formato de fecha inválido (use YYYY-MM-DD)')
            
        except Exception as e:
            logger.error(f"Error en validación de promoción: {str(e)}")
            errores.append('Error interno en validación')
        
        return errores


class PromocionService:
    """
    Servicio para gestión de promociones y su lógica de negocio.
    Maneja validaciones, cálculos y estados de promociones.
    """
    
    @staticmethod
    def obtener_promociones_con_estado():
        """
        Obtiene todas las promociones con su estado calculado.
        
        Returns:
            list: Lista de promociones con información de estado
        """
        try:
            from datetime import date
            hoy = date.today()
            
            promociones = Promocion.query.all()
            promociones_con_estado = []
            
            for promo in promociones:
                estado_info = PromocionService._calcular_estado_promocion(promo, hoy)
                promociones_con_estado.append({
                    'promocion': promo,
                    'estado': estado_info['estado'],
                    'estado_class': estado_info['estado_class'],
                    'dias_restantes': estado_info['dias_restantes'],
                    'activa': estado_info['activa']
                })
            
            return promociones_con_estado
            
        except Exception as e:
            logger.error(f"Error al obtener promociones con estado: {str(e)}")
            return []
    
    @staticmethod
    def _calcular_estado_promocion(promocion, fecha_actual):
        """
        Calcula el estado de una promoción específica.
        
        Args:
            promocion: Objeto Promocion
            fecha_actual: Fecha actual para comparar
            
        Returns:
            dict: Información del estado de la promoción
        """
        try:
            if promocion.fecha_inicio <= fecha_actual <= promocion.fecha_fin:
                dias_restantes = (promocion.fecha_fin - fecha_actual).days
                return {
                    'estado': 'Activa',
                    'estado_class': 'badge-available',
                    'dias_restantes': dias_restantes,
                    'activa': True
                }
            elif promocion.fecha_inicio > fecha_actual:
                dias_para_inicio = (promocion.fecha_inicio - fecha_actual).days
                return {
                    'estado': 'Próxima',
                    'estado_class': 'badge-warning',
                    'dias_restantes': dias_para_inicio,
                    'activa': False
                }
            else:  # promocion.fecha_fin < fecha_actual
                dias_vencida = (fecha_actual - promocion.fecha_fin).days
                return {
                    'estado': 'Vencida',
                    'estado_class': 'badge-unavailable',
                    'dias_restantes': -dias_vencida,
                    'activa': False
                }
                
        except Exception as e:
            logger.error(f"Error al calcular estado de promoción {promocion.id}: {str(e)}")
            return {
                'estado': 'Error',
                'estado_class': 'badge-secondary',
                'dias_restantes': 0,
                'activa': False
            }
    
    @staticmethod
    def obtener_estadisticas_promociones():
        """
        Calcula estadísticas de promociones para el dashboard.
        
        Returns:
            dict: Estadísticas de promociones
        """
        try:
            from datetime import date
            hoy = date.today()
            
            promociones = Promocion.query.all()
            
            if not promociones:
                return {
                    'total': 0,
                    'activas': 0,
                    'vencidas': 0,
                    'proximas': 0,
                    'descuento_promedio': 0,
                    'descuento_maximo': 0,
                    'descuento_minimo': 0
                }
            
            activas = []
            vencidas = []
            proximas = []
            descuentos = []
            
            for promo in promociones:
                descuentos.append(promo.descuento)
                
                if promo.fecha_inicio <= hoy <= promo.fecha_fin:
                    activas.append(promo)
                elif promo.fecha_inicio > hoy:
                    proximas.append(promo)
                else:
                    vencidas.append(promo)
            
            return {
                'total': len(promociones),
                'activas': len(activas),
                'vencidas': len(vencidas),
                'proximas': len(proximas),
                'descuento_promedio': sum(descuentos) / len(descuentos),
                'descuento_maximo': max(descuentos),
                'descuento_minimo': min(descuentos),
                'promociones_destacadas': sorted(promociones, key=lambda p: p.descuento, reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error(f"Error al calcular estadísticas de promociones: {str(e)}")
            return {
                'total': 0,
                'activas': 0,
                'vencidas': 0,
                'proximas': 0,
                'descuento_promedio': 0,
                'descuento_maximo': 0,
                'descuento_minimo': 0,
                'promociones_destacadas': []
            }
    
    @staticmethod
    def crear_promocion(descripcion, descuento, fecha_inicio, fecha_fin):
        """
        Crea una nueva promoción con validaciones de negocio.
        
        Args:
            descripcion: Descripción de la promoción
            descuento: Porcentaje de descuento
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            from datetime import datetime, date
            
            # Validaciones de negocio
            errores = ValidacionService.validar_promocion(descripcion, descuento, fecha_inicio, fecha_fin)
            
            if errores:
                return {
                    'success': False,
                    'message': ' '.join(errores)
                }
            
            # Convertir fechas
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Verificar conflictos con promociones existentes
            conflictos = PromocionService._verificar_conflictos_promocion(fecha_inicio, fecha_fin)
            if conflictos:
                logger.warning(f"Conflicto detectado al crear promoción: {conflictos}")
                return {
                    'success': False,
                    'message': f"Existe una promoción activa en el período seleccionado: {conflictos}"
                }
            
            # Crear promoción
            promocion = Promocion(
                descripcion=descripcion,
                descuento=float(descuento),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            db.session.add(promocion)
            db.session.commit()
            
            logger.info(f"Promoción creada exitosamente: {descripcion[:30]}...")
            return {
                'success': True,
                'message': 'Promoción creada exitosamente',
                'promocion_id': promocion.id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear promoción: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno del servidor'
            }
    
    @staticmethod
    def _verificar_conflictos_promocion(fecha_inicio, fecha_fin):
        """
        Verifica si existe conflicto con otras promociones activas.
        
        Args:
            fecha_inicio: Fecha de inicio de la nueva promoción
            fecha_fin: Fecha de fin de la nueva promoción
            
        Returns:
            str: Descripción del conflicto o None si no hay conflictos
        """
        try:
            conflicto = Promocion.query.filter(
                Promocion.fecha_inicio < fecha_fin,
                Promocion.fecha_fin > fecha_inicio
            ).first()
            
            if conflicto:
                return f"{conflicto.descripcion[:30]}... ({conflicto.fecha_inicio} - {conflicto.fecha_fin})"
            
            return None
            
        except Exception as e:
            logger.error(f"Error al verificar conflictos de promoción: {str(e)}")
            return None


class HabitacionService:
    """
    Servicio para gestión de habitaciones y su lógica de negocio.
    """
    
    @staticmethod
    def obtener_habitaciones_con_info():
        """
        Obtiene todas las habitaciones con información adicional calculada.
        
        Returns:
            list: Lista de habitaciones con datos enriquecidos
        """
        try:
            habitaciones = Habitacion.query.all()
            habitaciones_info = []
            
            for hab in habitaciones:
                info = HabitacionService._calcular_info_habitacion(hab)
                habitaciones_info.append({
                    'habitacion': hab,
                    'reservas_activas': info['reservas_activas'],
                    'proxima_disponible': info['proxima_disponible'],
                    'ocupacion_mes': info['ocupacion_mes'],
                    'ingresos_mes': info['ingresos_mes']
                })
            
            return habitaciones_info
            
        except Exception as e:
            logger.error(f"Error al obtener habitaciones con info: {str(e)}")
            return []
    
    @staticmethod
    def _calcular_info_habitacion(habitacion):
        """
        Calcula información adicional para una habitación.
        
        Args:
            habitacion: Objeto Habitacion
            
        Returns:
            dict: Información calculada de la habitación
        """
        try:
            from datetime import date, timedelta
            hoy = date.today()
            inicio_mes = hoy.replace(day=1)
            
            # Reservas activas
            reservas_activas = Reserva.query.filter(
                Reserva.habitacion_id == habitacion.id,
                Reserva.estado.in_(['pendiente', 'confirmada']),
                Reserva.fecha_fin >= hoy
            ).count()
            
            # Próxima fecha disponible
            proxima_reserva = Reserva.query.filter(
                Reserva.habitacion_id == habitacion.id,
                Reserva.estado.in_(['pendiente', 'confirmada']),
                Reserva.fecha_inicio >= hoy
            ).order_by(Reserva.fecha_inicio).first()
            
            proxima_disponible = proxima_reserva.fecha_fin if proxima_reserva else hoy
            
            # Ocupación del mes actual
            reservas_mes = Reserva.query.filter(
                Reserva.habitacion_id == habitacion.id,
                Reserva.estado == 'confirmada',
                Reserva.fecha_inicio >= inicio_mes,
                Reserva.fecha_inicio < hoy
            ).all()
            
            dias_ocupados = sum(
                min((r.fecha_fin - max(r.fecha_inicio, inicio_mes)).days, 30)
                for r in reservas_mes
            )
            
            ocupacion_mes = (dias_ocupados / hoy.day) * 100 if hoy.day > 0 else 0
            
            # Ingresos del mes
            ingresos_mes = sum(
                habitacion.precio * min((r.fecha_fin - max(r.fecha_inicio, inicio_mes)).days, 30)
                for r in reservas_mes
            )
            
            return {
                'reservas_activas': reservas_activas,
                'proxima_disponible': proxima_disponible,
                'ocupacion_mes': round(ocupacion_mes, 1),
                'ingresos_mes': ingresos_mes
            }
            
        except Exception as e:
            logger.error(f"Error al calcular info de habitación {habitacion.id}: {str(e)}")
            return {
                'reservas_activas': 0,
                'proxima_disponible': date.today(),
                'ocupacion_mes': 0,
                'ingresos_mes': 0
            }
    
    @staticmethod
    def crear_habitacion(numero, tipo, precio, descripcion, disponible, tipo_id):
        """
        Crea una nueva habitación con validaciones de negocio.
        
        Args:
            numero: Número de la habitación
            tipo: Tipo de habitación
            precio: Precio por noche
            descripcion: Descripción de la habitación
            disponible: Si está disponible
            tipo_id: ID del tipo de habitación
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validaciones de negocio
            errores = ValidacionService.validar_habitacion(numero, tipo, precio, descripcion, tipo_id)
            
            if errores:
                return {
                    'success': False,
                    'message': ' '.join(errores)
                }
            
            # Verificar duplicados
            habitacion_existente = Habitacion.query.filter_by(numero=numero).first()
            if habitacion_existente:
                return {
                    'success': False,
                    'message': f'Ya existe una habitación con el número {numero}'
                }
            
            # Crear habitación
            habitacion = Habitacion(
                numero=numero,
                tipo=tipo,
                precio=float(precio),
                descripcion=descripcion,
                disponible=disponible,
                tipo_id=tipo_id
            )
            
            db.session.add(habitacion)
            db.session.commit()
            
            logger.info(f"Habitación {numero} creada exitosamente")
            return {
                'success': True,
                'message': 'Habitación creada exitosamente',
                'habitacion_id': habitacion.id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear habitación: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno del servidor'
            }
    
    @staticmethod
    def verificar_disponibilidad(habitacion_id, fecha_inicio, fecha_fin, excluir_reserva_id=None):
        """
        Verifica si una habitación está disponible en un período.
        
        Args:
            habitacion_id: ID de la habitación
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            excluir_reserva_id: ID de reserva a excluir (para ediciones)
            
        Returns:
            dict: Resultado de la verificación
        """
        try:
            from datetime import datetime
            
            # Convertir fechas si son strings
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Buscar conflictos
            query = Reserva.query.filter(
                Reserva.habitacion_id == habitacion_id,
                Reserva.estado.in_(['pendiente', 'confirmada']),
                Reserva.fecha_inicio < fecha_fin,
                Reserva.fecha_fin > fecha_inicio
            )
            
            if excluir_reserva_id:
                query = query.filter(Reserva.id != excluir_reserva_id)
            
            conflicto = query.first()
            
            if conflicto:
                return {
                    'disponible': False,
                    'conflicto': f"Reserva #{conflicto.id} del {conflicto.fecha_inicio} al {conflicto.fecha_fin}"
                }
            
            return {'disponible': True, 'conflicto': None}
            
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {str(e)}")
            return {
                'disponible': False,
                'conflicto': 'Error al verificar disponibilidad'
            }
    
    @staticmethod
    def validar_habitacion(numero, tipo, precio, descripcion, tipo_id):
        """
        Valida los datos de una habitación.
        
        Args:
            numero: Número de la habitación
            tipo: Tipo de habitación
            precio: Precio por noche
            descripcion: Descripción
            tipo_id: ID del tipo de habitación
            
        Returns:
            list: Lista de errores de validación
        """
        errores = []
        
        try:
            # Validar número
            if not numero or not str(numero).strip():
                errores.append('El número de habitación es requerido')
            elif len(str(numero).strip()) > 10:
                errores.append('El número de habitación no puede exceder 10 caracteres')
            
            # Validar tipo
            if not tipo or not tipo.strip():
                errores.append('El tipo de habitación es requerido')
            elif len(tipo.strip()) > 50:
                errores.append('El tipo no puede exceder 50 caracteres')
            
            # Validar precio
            try:
                precio_float = float(precio)
                if precio_float <= 0:
                    errores.append('El precio debe ser mayor a cero')
                elif precio_float > 10000:
                    errores.append('El precio no puede exceder $10,000 por noche')
            except (ValueError, TypeError):
                errores.append('El precio debe ser un número válido')
            
            # Validar descripción
            if descripcion and len(descripcion) > 500:
                errores.append('La descripción no puede exceder 500 caracteres')
            
            # Validar tipo_id
            if not tipo_id:
                errores.append('Debe seleccionar un tipo de habitación')
            else:
                try:
                    from app.models import TipoHabitacion
                    tipo_existe = TipoHabitacion.query.get(int(tipo_id))
                    if not tipo_existe:
                        errores.append('El tipo de habitación seleccionado no existe')
                except (ValueError, TypeError):
                    errores.append('ID de tipo de habitación inválido')
            
        except Exception as e:
            logger.error(f"Error en validación de habitación: {str(e)}")
            errores.append('Error interno en validación')
        
        return errores
