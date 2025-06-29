"""
Utilidades y funciones auxiliares para la aplicación
"""
import re
from datetime import datetime, date
from flask import flash

def validar_email(email):
    """
    Valida el formato de un email
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_password(password):
    """
    Valida que la contraseña cumpla con criterios mínimos de seguridad
    """
    errores = []
    
    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres")
    
    if not re.search(r'[A-Z]', password):
        errores.append("La contraseña debe contener al menos una letra mayúscula")
    
    if not re.search(r'[a-z]', password):
        errores.append("La contraseña debe contener al menos una letra minúscula")
    
    if not re.search(r'\d', password):
        errores.append("La contraseña debe contener al menos un número")
    
    return errores

def validar_fechas_reserva(fecha_inicio, fecha_fin):
    """
    Valida las fechas de una reserva
    """
    errores = []
    
    # Convertir strings a objetos date si es necesario
    if isinstance(fecha_inicio, str):
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        except ValueError:
            errores.append("Formato de fecha de inicio inválido")
            return errores
    
    if isinstance(fecha_fin, str):
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            errores.append("Formato de fecha de fin inválido")
            return errores
    
    # Validaciones
    if fecha_inicio < date.today():
        errores.append("La fecha de inicio no puede ser anterior a hoy")
    
    if fecha_fin <= fecha_inicio:
        errores.append("La fecha de fin debe ser posterior a la fecha de inicio")
    
    # Validar que no sea una estancia muy larga (más de 30 días)
    diferencia = (fecha_fin - fecha_inicio).days
    if diferencia > 30:
        errores.append("La estancia no puede ser mayor a 30 días")
    
    return errores

def validar_precio(precio):
    """
    Valida que el precio sea un número positivo válido
    """
    try:
        precio_float = float(precio)
        if precio_float < 0:
            return False, "El precio no puede ser negativo"
        if precio_float > 10000:
            return False, "El precio parece demasiado alto"
        return True, None
    except (ValueError, TypeError):
        return False, "El precio debe ser un número válido"

def sanitizar_texto(texto):
    """
    Limpia y sanitiza texto de entrada
    """
    if not texto:
        return ""
    
    # Eliminar espacios al inicio y final
    texto = texto.strip()
    
    # Eliminar caracteres especiales peligrosos
    caracteres_peligrosos = ['<', '>', '"', "'", '&']
    for char in caracteres_peligrosos:
        texto = texto.replace(char, '')
    
    return texto

def calcular_costo_reserva(habitacion, fecha_inicio, fecha_fin, servicios_extra=None):
    """
    Calcula el costo total de una reserva
    """
    try:
        # Convertir fechas si son strings
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Calcular días
        dias = (fecha_fin - fecha_inicio).days
        if dias <= 0:
            return 0
        
        # Costo de habitación
        costo_habitacion = habitacion.precio * dias
        
        # Costo de servicios extra
        costo_servicios = 0
        if servicios_extra:
            for servicio in servicios_extra:
                costo_servicios += servicio.precio
        
        return costo_habitacion + costo_servicios
    
    except Exception:
        return 0

def formatear_moneda(monto):
    """
    Formatea un monto como moneda
    """
    try:
        return f"${float(monto):.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def validar_campos_requeridos(datos, campos_requeridos):
    """
    Valida que todos los campos requeridos estén presentes y no vacíos
    """
    errores = []
    
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo] or str(datos[campo]).strip() == '':
            errores.append(f"El campo '{campo}' es requerido")
    
    return errores
