"""
Helpers de Vista (View Helpers) - Capa de Presentación
=====================================================

Este módulo contiene funciones helper para las vistas/templates.
Separa la lógica de presentación de los templates para mantener
una arquitectura MVC más limpia.

Author: Equipo Hotel Paraíso Real
Version: 2.0
"""

import logging
from datetime import date, datetime
try:
    from markupsafe import Markup
except ImportError:
    from flask import Markup

logger = logging.getLogger(__name__)

class ViewHelper:
    """
    Clase con métodos estáticos para ayudar en la presentación de datos.
    """
    
    @staticmethod
    def formatear_fecha(fecha, formato='%d/%m/%Y'):
        """
        Formatea una fecha para mostrar en templates.
        
        Args:
            fecha: Objeto date o datetime
            formato: Formato de fecha deseado
            
        Returns:
            str: Fecha formateada o 'N/A' si es None
        """
        if not fecha:
            return 'N/A'
        
        try:
            if isinstance(fecha, datetime):
                fecha = fecha.date()
            return fecha.strftime(formato)
        except Exception as e:
            logger.error(f"Error al formatear fecha: {str(e)}")
            return 'Error'
    
    @staticmethod
    def formatear_moneda(monto, simbolo='$'):
        """
        Formatea un monto como moneda.
        
        Args:
            monto: Cantidad a formatear
            simbolo: Símbolo de moneda
            
        Returns:
            str: Monto formateado
        """
        try:
            return f"{simbolo}{float(monto):,.2f}"
        except (ValueError, TypeError):
            return f"{simbolo}0.00"
    
    @staticmethod
    def calcular_duracion_reserva(fecha_inicio, fecha_fin):
        """
        Calcula la duración en días de una reserva.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            int: Número de días
        """
        try:
            if not fecha_inicio or not fecha_fin:
                return 0
            
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            return (fecha_fin - fecha_inicio).days
        except Exception as e:
            logger.error(f"Error al calcular duración: {str(e)}")
            return 0
    
    @staticmethod
    def obtener_clase_estado(estado):
        """
        Obtiene la clase CSS apropiada para un estado.
        
        Args:
            estado: Estado a evaluar
            
        Returns:
            str: Clase CSS
        """
        clases_estado = {
            'activa': 'badge-success',
            'active': 'badge-success',
            'confirmada': 'badge-success',
            'pendiente': 'badge-warning',
            'pending': 'badge-warning',
            'próxima': 'badge-info',
            'vencida': 'badge-danger',
            'expired': 'badge-danger',
            'cancelada': 'badge-secondary',
            'cancelled': 'badge-secondary'
        }
        
        return clases_estado.get(estado.lower() if estado else '', 'badge-secondary')
    
    @staticmethod
    def truncar_texto(texto, longitud=50, sufijo='...'):
        """
        Trunca texto a una longitud específica.
        
        Args:
            texto: Texto a truncar
            longitud: Longitud máxima
            sufijo: Sufijo a agregar si se trunca
            
        Returns:
            str: Texto truncado
        """
        if not texto:
            return ''
        
        if len(texto) <= longitud:
            return texto
        
        return texto[:longitud] + sufijo
    
    @staticmethod
    def generar_badge_disponibilidad(disponible):
        """
        Genera un badge HTML para mostrar disponibilidad.
        
        Args:
            disponible: Boolean de disponibilidad
            
        Returns:
            Markup: HTML del badge
        """
        if disponible:
            return Markup('<span class="badge badge-success"><i class="fas fa-check"></i> Disponible</span>')
        else:
            return Markup('<span class="badge badge-danger"><i class="fas fa-times"></i> No disponible</span>')
    
    @staticmethod
    def calcular_porcentaje_ocupacion(dias_ocupados, total_dias):
        """
        Calcula el porcentaje de ocupación.
        
        Args:
            dias_ocupados: Días ocupados
            total_dias: Total de días
            
        Returns:
            float: Porcentaje de ocupación
        """
        try:
            if total_dias == 0:
                return 0
            return round((dias_ocupados / total_dias) * 100, 1)
        except Exception:
            return 0
    
    @staticmethod
    def obtener_icono_tipo_habitacion(tipo):
        """
        Obtiene el icono FontAwesome apropiado para un tipo de habitación.
        
        Args:
            tipo: Tipo de habitación
            
        Returns:
            str: Clase de icono
        """
        iconos = {
            'sencilla': 'fas fa-bed',
            'doble': 'fas fa-bed',
            'suite': 'fas fa-crown',
            'familiar': 'fas fa-home',
            'presidencial': 'fas fa-star',
            'ejecutiva': 'fas fa-briefcase'
        }
        
        return iconos.get(tipo.lower() if tipo else '', 'fas fa-door-open')
    
    @staticmethod
    def generar_color_progreso(porcentaje):
        """
        Genera un color apropiado para una barra de progreso.
        
        Args:
            porcentaje: Porcentaje a evaluar
            
        Returns:
            str: Clase de color
        """
        if porcentaje >= 80:
            return 'bg-success'
        elif porcentaje >= 60:
            return 'bg-warning'
        elif porcentaje >= 40:
            return 'bg-info'
        else:
            return 'bg-danger'
    
    @staticmethod
    def obtener_clase_alerta(category):
        """
        Obtiene la clase CSS apropiada para una alerta.
        
        Args:
            category: Categoría del mensaje flash
            
        Returns:
            str: Clase CSS de Bootstrap
        """
        clases_alerta = {
            'error': 'danger',
            'danger': 'danger',
            'success': 'success',
            'warning': 'warning',
            'info': 'info',
            'primary': 'primary',
            'secondary': 'secondary'
        }
        
        return clases_alerta.get(category.lower() if category else '', 'info')
    
    @staticmethod
    def obtener_icono_alerta(category):
        """
        Obtiene el icono FontAwesome apropiado para una alerta.
        
        Args:
            category: Categoría del mensaje flash
            
        Returns:
            str: Clase de icono FontAwesome
        """
        iconos_alerta = {
            'error': 'exclamation-circle',
            'danger': 'exclamation-triangle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'star',
            'secondary': 'cog'
        }
        
        return iconos_alerta.get(category.lower() if category else '', 'info-circle')


class PromotionHelper:
    """
    Helper específico para promociones.
    """
    
    @staticmethod
    def calcular_ahorro(precio_original, descuento):
        """
        Calcula el ahorro de una promoción.
        
        Args:
            precio_original: Precio original
            descuento: Porcentaje de descuento
            
        Returns:
            dict: Información del ahorro
        """
        try:
            descuento_decimal = float(descuento) / 100
            ahorro = float(precio_original) * descuento_decimal
            precio_final = float(precio_original) - ahorro
            
            return {
                'precio_original': precio_original,
                'ahorro': ahorro,
                'precio_final': precio_final,
                'descuento_porcentaje': descuento
            }
        except Exception as e:
            logger.error(f"Error al calcular ahorro: {str(e)}")
            return {
                'precio_original': precio_original,
                'ahorro': 0,
                'precio_final': precio_original,
                'descuento_porcentaje': 0
            }
    
    @staticmethod
    def obtener_urgencia_promocion(dias_restantes):
        """
        Determina el nivel de urgencia de una promoción.
        
        Args:
            dias_restantes: Días restantes de la promoción
            
        Returns:
            dict: Información de urgencia
        """
        if dias_restantes <= 0:
            return {
                'urgencia': 'vencida',
                'clase': 'text-danger',
                'mensaje': 'Promoción vencida'
            }
        elif dias_restantes <= 3:
            return {
                'urgencia': 'alta',
                'clase': 'text-danger',
                'mensaje': f'¡Solo quedan {dias_restantes} días!'
            }
        elif dias_restantes <= 7:
            return {
                'urgencia': 'media',
                'clase': 'text-warning',
                'mensaje': f'Quedan {dias_restantes} días'
            }
        else:
            return {
                'urgencia': 'baja',
                'clase': 'text-info',
                'mensaje': f'{dias_restantes} días disponibles'
            }


# Función para registrar los helpers en Jinja2
def register_view_helpers(app):
    """
    Registra los view helpers como funciones disponibles en Jinja2.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.jinja_env.globals.update(
        formatear_fecha=ViewHelper.formatear_fecha,
        formatear_moneda=ViewHelper.formatear_moneda,
        calcular_duracion=ViewHelper.calcular_duracion_reserva,
        obtener_clase_estado=ViewHelper.obtener_clase_estado,
        truncar_texto=ViewHelper.truncar_texto,
        badge_disponibilidad=ViewHelper.generar_badge_disponibilidad,
        porcentaje_ocupacion=ViewHelper.calcular_porcentaje_ocupacion,
        icono_tipo_habitacion=ViewHelper.obtener_icono_tipo_habitacion,
        color_progreso=ViewHelper.generar_color_progreso,
        calcular_ahorro=PromotionHelper.calcular_ahorro,
        urgencia_promocion=PromotionHelper.obtener_urgencia_promocion
    )
