# 📋 Manual de Usuario - Hotel Paraíso Real

## 🏨 Sistema de Reservas Hoteleras

### 📖 Introducción

Este manual está diseñado para ayudar a los usuarios a aprovechar al máximo el sistema de gestión hotelera **Hotel Paraíso Real**. El sistema permite gestionar reservas, habitaciones y servicios de forma intuitiva y eficiente.

---

## 🚀 Acceso al Sistema

### 1. **Página de Inicio**
- **URL:** `http://localhost:5000`
- **Navegadores compatibles:** Chrome, Firefox, Safari, Edge
- **Requisitos:** Conexión a internet activa

### 2. **Tipos de Usuario**

#### 👤 **Cliente**
- **Email:** `cliente@hotel.com`
- **Contraseña:** `cliente123`
- **Funciones:** Explorar habitaciones, realizar reservas, gestionar perfil

#### 🔧 **Empleado**
- **Email:** `empleado@hotel.com`
- **Contraseña:** `empleado123`
- **Funciones:** Gestión de reservas, habitaciones, servicios

#### 👑 **Administrador**
- **Email:** `admin@hotel.com`
- **Contraseña:** `admin123`
- **Funciones:** Acceso completo al sistema, reportes, configuraciones

---

## 👤 Funcionalidades del Cliente

### 🏠 **Dashboard Principal**

Al iniciar sesión como cliente, accederás a un dashboard moderno con:

#### ✨ **Características Principales:**
- **Hero Section:** Bienvenida personalizada con estadísticas
- **Quick Actions:** Acceso rápido a funciones principales
- **Galería de Habitaciones:** Vista premium de habitaciones disponibles
- **Mis Reservas:** Historial y reservas activas
- **Ofertas Especiales:** Promociones disponibles

#### 🔍 **Explorar Habitaciones**

1. **Filtros Avanzados:**
   - Tipo de habitación (Suite Premium, Deluxe, Estándar)
   - Rango de precios ($0-$50, $51-$100, $101-$200, $201+)
   - Vista de lista o cuadrícula

2. **Tarjetas de Habitación:**
   - Imagen de alta calidad
   - Información básica (tipo, precio, capacidad)
   - Badges de estado (Disponible, Oferta Especial)
   - Amenidades incluidas
   - Calificación y reseñas

#### 🖱️ **Ver Detalles de Habitación**

**Método 1: Modal Premium**
1. Click en "Ver Detalles" en cualquier habitación
2. Se abre un modal con información completa:
   - Imagen principal con galería
   - Especificaciones técnicas
   - Descripción detallada
   - Amenidades premium
   - Formulario de reserva rápida

**Método 2: Sidebar Deslizante** (Funcionalidad Premium)
1. Click en el botón específico del sidebar
2. Panel deslizante desde la derecha con:
   - Información condensada
   - Acciones rápidas (Comparar, Compartir)
   - Formulario de reserva inmediata

#### 📅 **Realizar Reserva**

**Desde el Dashboard:**
1. Selecciona habitación → "Ver Detalles"
2. En el modal, completa el formulario:
   - **Check-in:** Fecha de entrada (mínimo hoy)
   - **Check-out:** Fecha de salida (mínimo mañana)
   - **Huéspedes:** Según capacidad de la habitación
   - **Servicios extra:** (Opcional)
     - Desayuno Continental (+$25)
     - Traslado Aeropuerto (+$40)
     - Masaje Relajante (+$80)
     - Cena Romántica (+$120)
3. **Resumen automático:** El sistema calcula el total
4. Click "Confirmar Reserva"
5. ✅ Confirmación instantánea

**Validaciones Automáticas:**
- ✅ Fechas válidas (salida > entrada)
- ✅ Disponibilidad de habitación
- ✅ Capacidad máxima respetada
- ✅ Servicios compatibles

#### 📊 **Mis Reservas**

En la sección "Mis Reservas" puedes:

1. **Ver reservas activas:**
   - Número de reserva
   - Habitación asignada
   - Fechas de estadía
   - Estado actual (Pendiente/Confirmada/Cancelada)
   - Servicios incluidos

2. **Gestionar reservas:**
   - Editar fechas (según disponibilidad)
   - Agregar/quitar servicios
   - Ver detalles completos
   - Cancelar reserva

#### 🎁 **Ofertas Especiales**

- **Promociones activas:** Descuentos vigentes
- **Ofertas por temporada:** Paquetes especiales
- **Programas de fidelidad:** Beneficios exclusivos

### 🔧 **Configuración de Perfil**

1. **Información personal:**
   - Nombre completo
   - Email de contacto
   - Preferencias de comunicación

2. **Historial de reservas:**
   - Todas las reservas pasadas
   - Estadísticas de uso
   - Puntos de fidelidad

---

## 🔧 Funcionalidades del Empleado

### 📋 **Panel de Gestión**

Los empleados tienen acceso a:

#### 🏨 **Gestión de Habitaciones**
- **Listar habitaciones:** `/habitaciones`
- **Nueva habitación:** Formulario completo
- **Editar habitación:** Modificar datos existentes
- **Estado de habitaciones:** Disponible/Ocupada/Mantenimiento

#### 📅 **Gestión de Reservas**
- **Ver todas las reservas:** `/reservas`
- **Crear reserva:** Para clientes sin cuenta
- **Editar reserva:** Modificar fechas, servicios
- **Cancelar reserva:** Con confirmación

#### 👥 **Gestión de Servicios**
- **Servicios extra:** Crear, editar, eliminar
- **Precios dinámicos:** Actualización de tarifas
- **Disponibilidad:** Control de stock

#### 📊 **Reportes Básicos**
- Ocupación diaria
- Ingresos por período
- Servicios más solicitados

---

## 👑 Funcionalidades del Administrador

### 🎛️ **Dashboard Administrativo Completo**

**URL:** `/dashboard/admin`

#### 📈 **Panel de Estadísticas**
- **Métricas en tiempo real:**
  - Total de habitaciones
  - Reservas activas
  - Usuarios registrados
  - Ingresos mensuales
  - Tasa de ocupación

#### 🗂️ **Gestión Completa de Entidades**

**Navegación por pestañas:**

1. **📊 Dashboard**
   - Estadísticas generales
   - Reservas recientes
   - Gráfico de ocupación
   - Métricas de rendimiento

2. **🏨 Habitaciones**
   - CRUD completo de habitaciones
   - Gestión de tipos de habitación
   - Control de precios y disponibilidad
   - Asignación de amenidades

3. **📅 Reservas**
   - Todas las reservas del sistema
   - Filtros avanzados por fecha, estado, cliente
   - Edición masiva de reservas
   - Reportes de ocupación

4. **👥 Usuarios**
   - Gestión de todos los usuarios
   - Asignación de roles (Cliente/Empleado/Admin)
   - Control de accesos
   - Historial de actividades

5. **🛎️ Servicios Extra**
   - Crear nuevos servicios
   - Configurar precios y descripción
   - Control de disponibilidad
   - Estadísticas de uso

6. **🎁 Promociones**
   - Crear ofertas y descuentos
   - Configurar fechas de validez
   - Aplicar a tipos específicos de habitación
   - Seguimiento de efectividad

7. **⭐ Opiniones**
   - Moderar comentarios de clientes
   - Responder a reseñas
   - Análisis de satisfacción
   - Reportes de calidad

#### 🔒 **Seguridad y Configuración**
- Control de accesos por rol
- Logs de actividad del sistema
- Configuraciones globales
- Respaldos de base de datos

---

## 🛠️ Funcionalidades Técnicas

### 🎨 **Interfaz de Usuario**

#### **Diseño Responsive**
- ✅ **Móvil:** Optimizado para pantallas pequeñas
- ✅ **Tablet:** Interfaz adaptada para touch
- ✅ **Desktop:** Experiencia completa

#### **Características Visuales**
- **Paleta de colores:** Azules y grises profesionales
- **Tipografía:** Inter + Playfair Display para elegancia
- **Iconografía:** Font Awesome 6.4.0
- **Animaciones:** Transiciones suaves de 60fps

#### **Accesibilidad**
- ⌨️ Navegación por teclado
- 🔍 Alto contraste
- 📱 Compatible con lectores de pantalla
- 🎯 Elementos focusables claramente identificados

### 🔧 **Funcionalidades Avanzadas**

#### **Modal de Detalles Premium**
- **Apertura suave:** Animación de escala + fade
- **Contenido dinámico:** Poblado automáticamente
- **Integración con reservas:** Formulario funcional
- **Responsive:** Adaptado a todos los dispositivos

#### **Sidebar Deslizante**
- **Animación fluida:** Deslizamiento desde la derecha
- **Overlay con blur:** Efecto de desenfoque del fondo
- **Contenido condensado:** Información esencial
- **Acciones rápidas:** Comparar, compartir, reservar

#### **Sistema de Filtros**
- **Filtro por tipo:** Dinámico según tipos disponibles
- **Filtro por precio:** Rangos predefinidos
- **Vista dual:** Cuadrícula o lista
- **Resultados instantáneos:** Sin recarga de página

### 📊 **Gestión de Datos**

#### **Validaciones**
- **Frontend:** JavaScript para UX inmediata
- **Backend:** Python/Flask para seguridad
- **Base de datos:** Constraints SQLite

#### **Estados de Reserva**
- **Pendiente:** Recién creada, esperando confirmación
- **Confirmada:** Verificada y lista
- **Cancelada:** Anulada por cliente/admin
- **Completada:** Estadía finalizada

---

## 🔍 Resolución de Problemas

### ❓ **Problemas Comunes**

#### **No puedo iniciar sesión**
1. ✅ Verifica las credenciales
2. ✅ Revisa que el servidor esté activo
3. ✅ Limpia caché del navegador
4. ❌ Si persiste: Contacta al administrador

#### **No se cargan las habitaciones**
1. ✅ Verifica conexión a internet
2. ✅ Refresca la página (F5)
3. ✅ Revisa consola del navegador (F12)
4. ❌ Si persiste: Problema del servidor

#### **Error al hacer reserva**
1. ✅ Verifica que las fechas sean válidas
2. ✅ Confirma disponibilidad de la habitación
3. ✅ Revisa que todos los campos estén completos
4. ❌ Si persiste: Habitación puede estar ocupada

#### **Modal no se abre**
1. ✅ Verifica que JavaScript esté habilitado
2. ✅ Refresca la página completamente
3. ✅ Prueba en modo incógnito
4. ❌ Si persiste: Problema de compatibilidad

### 🆘 **Contacto de Soporte**

**Desarrollador:** GitHub Copilot  
**Email:** soporte@hotelparaisoreal.com  
**Teléfono:** +1 (555) 123-4567  
**Horario:** Lunes a Viernes, 9:00 AM - 6:00 PM  

---

## 🎯 **Consejos de Uso**

### ✨ **Para Maximizar la Experiencia**

1. **Explora el dashboard completo** antes de hacer reservas
2. **Usa los filtros** para encontrar habitaciones específicas
3. **Revisa las amenidades** incluidas en cada habitación
4. **Aprovecha las ofertas especiales** disponibles
5. **Guarda tus habitaciones favoritas** para comparar
6. **Verifica las fechas** antes de confirmar reservas

### 🎨 **Funcionalidades Premium**

1. **Sidebar deslizante:** Para vista rápida sin perder contexto
2. **Modal de detalles:** Para información completa
3. **Reserva rápida:** Formulario integrado en los modales
4. **Compartir habitaciones:** Usando Web Share API
5. **Vista de galería:** Para ver múltiples fotos
6. **Comparar habitaciones:** Funcionalidad avanzada

---

## 📱 **Compatibilidad**

### 🌐 **Navegadores Soportados**
- ✅ **Chrome** 90+ (Recomendado)
- ✅ **Firefox** 88+
- ✅ **Safari** 14+
- ✅ **Edge** 90+

### 📱 **Dispositivos**
- ✅ **Smartphones** (320px+)
- ✅ **Tablets** (768px+)
- ✅ **Laptops** (1024px+)
- ✅ **Desktops** (1200px+)

### ⚡ **Rendimiento**
- **Tiempo de carga:** < 3 segundos
- **Animaciones:** 60 FPS constantes
- **Tamaño de página:** < 2MB
- **Compatibilidad offline:** Limitada

---

## 🎉 **¡Disfruta tu Experiencia!**

El sistema **Hotel Paraíso Real** está diseñado para ofrecerte la mejor experiencia de reserva hotelera. Cada funcionalidad ha sido cuidadosamente desarrollada para ser intuitiva, rápida y elegante.

**🌟 ¡Esperamos que disfrutes usando nuestro sistema!**

---

*Manual de Usuario v1.0 - Hotel Paraíso Real*  
*Última actualización: Junio 2025*
