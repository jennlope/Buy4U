# 🛒 Buy4U - Plataforma de E-commerce de Dispositivos Electrónicos

Buy4U es una plataforma web de comercio electrónico desarrollada con **Django** enfocada en la venta de dispositivos electrónicos (smartphones, laptops y tablets). Ofrece una experiencia de compra fácil, rápida y segura con soporte multiidioma (español/inglés).

## 📋 Requisitos Previos

- **Python 3.10+**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)
- **Base de datos**: SQLite (incluida en Django por defecto)
- **GNU gettext** (para traducciones) - Opcional pero recomendado

## 🚀 Instalación y Configuración

### 1. **Clonar o descargar el proyecto**

```bash
cd c:\Users\Usuario\Documents\Personal\EAFIT\Semestres\SeptimoSemestre\P2\Buy4U
```

### 2. **Crear un entorno virtual**

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate.bat

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

**Si no tienes `requirements.txt`, instala manualmente:**

```bash
pip install Django==4.2
pip install djangorestframework
pip install pillow
pip install requests
pip install python-dotenv
```

### 4. **Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
WEATHER_API_KEY=tu-api-key-openweathermap
```

### 5. **Aplicar migraciones de base de datos**

```bash
python manage.py migrate
```

### 6. **Crear superusuario (administrador)**

```bash
python manage.py createsuperuser
# Ingresa los datos solicitados (usuario, email, contraseña)
```

### 7. **Recopilar archivos estáticos**

```bash
python manage.py collectstatic --noinput
```

### 8. **Compilar traducciones (Opcional pero recomendado)**

```bash
# Genera archivos de traducción
python manage.py makemessages -l es -l en

# Compila traducciones a formato binario
python manage.py compilemessages
```

**Si tienes error de `msguniq`/`msgfmt`:**
- Descarga GNU gettext: https://mlocati.github.io/articles/gettext-iconv-windows.html
- O salta este paso (las traducciones funcionarán desde archivos `.po`)

## ▶️ Ejecutar la Aplicación

```bash
python manage.py runserver
```

Accede a la aplicación en: **http://127.0.0.1:8000/**

### Credenciales de Administrador

- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: El que creaste en el paso 6
- **Contraseña**: La que configuraste

## 📁 Estructura del Proyecto

```
Buy4U/
├── buy4u/                  # Configuración principal del proyecto
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # WSGI para producción
├── shop/                   # App principal de tienda
│   ├── models.py           # Modelos (Product, Order, etc.)
│   ├── views.py            # Vistas
│   ├── urls.py             # URLs de shop
│   └── templates/          # Plantillas HTML
├── accounts/               # App de autenticación
│   ├── models.py           # Modelo de usuario personalizado
│   ├── views.py            # Login/Register
│   └── templates/          # Plantillas auth
├── orders/                 # App de órdenes/carrito
│   ├── models.py           # Modelo de órdenes
│   ├── views.py            # Lógica de carrito
│   └── templates/          # Plantillas de órdenes
├── locale/                 # Archivos de traducción
│   └── es/LC_MESSAGES/     # Traducción al español
│       ├── django.po       # Archivo fuente (editable)
│       └── django.mo       # Archivo compilado
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   ├── js/
│   └── img/
├── templates/              # Templates base
├── db.sqlite3             # Base de datos SQLite
├── manage.py              # Script de gestión de Django
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Este archivo
```

## 🌐 Características Principales

### 👥 Autenticación
- Registro de nuevos usuarios
- Login/Logout
- Perfiles de usuario
- Roles de administrador

### 🛍️ Tienda
- Catálogo de productos (Smartphones, Laptops, Tablets)
- Búsqueda y filtrado por categoría y precio
- Página de detalle del producto
- Sistema de reseñas y calificaciones (★★★★★)
- Productos destacados automáticamente según rating

### 🛒 Carrito de Compras
- Agregar/eliminar productos
- Actualizar cantidades
- Cálculo automático de total
- Validación de stock

### 📦 Órdenes
- Historial de compras
- Estado de órdenes (Pendiente, En proceso, Completada)
- Pasarela de pago básica
- Confirmación de pedidos

### 📊 Panel Administrativo
- Gestión de productos
- Reporte de ventas
- Estadísticas de uso
- Gráficos de tendencias
- Exportación a CSV

### 🌍 Multiidioma
- **Español** (es) e **Inglés** (en)
- Selector de idioma en la navegación
- Todas las cadenas traducidas dinámicamente

### 🌦️ Información del Clima
- Muestra clima de Medellín en tiempo real
- Integración con API OpenWeatherMap

### 🔍 Comparador de Productos
- Comparar especificaciones de productos
- Vista lado a lado

## 📝 Uso de la Aplicación

### Como Cliente

1. **Registrarse**: Haz clic en "Register" en la navegación
2. **Navegar productos**: Ve a "Shop" para ver el catálogo
3. **Filtrar**: Usa los filtros de categoría y precio
4. **Agregar al carrito**: Haz clic en "Add to Cart"
5. **Comprar**: Ve al carrito y procede al pago
6. **Ver historial**: En "Purchase history" ves tus compras anteriores

### Como Administrador

1. Accede a http://127.0.0.1:8000/admin/
2. Ve a "Shop" → "Products" para gestionar productos
3. Ve a "Orders" para ver órdenes
4. Accede al dashboard de reportes en http://127.0.0.1:8000/admin_product/reports/

## 🔧 Configuración Avanzada

### Cambiar base de datos a PostgreSQL

```bash
pip install psycopg2-binary
```

En `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'buy4u_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Agregar API Key de OpenWeatherMap

```python
# settings.py
OPENWEATHER_API_KEY = 'tu_api_key_aqui'
```

## 📦 Dependencias Principales

- **Django 4.2**: Framework web
- **Django REST Framework**: API REST
- **Pillow**: Procesamiento de imágenes
- **Requests**: Solicitudes HTTP
- **python-dotenv**: Manejo de variables de entorno

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
pip install -r requirements.txt
# o
pip install Django==4.2
```

### Error: "No such table: shop_product"
```bash
python manage.py migrate
```

### Error: "msguniq not found" (traducciones)
Descarga GNU gettext o desactiva compilaciones de mensajes.

### Puerto 8000 ya está en uso
```bash
python manage.py runserver 8001
```

### Problemas con archivos estáticos (CSS/JS no se ve)

```bash
python manage.py collectstatic --noinput
```

En `settings.py` asegúrate de tener:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 📚 Documentación Útil

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Font Awesome Icons](https://fontawesome.com/icons)

## 👨‍💻 Desarrolladores

Equipo de desarrollo Buy4U - EAFIT Semestre 7

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 📞 Soporte

Para reportar bugs o sugerencias, abre un issue en el repositorio del proyecto.

---

**Última actualización**: Noviembre 5, 2025