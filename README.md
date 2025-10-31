# 🛒 Buy4U 
Buy4U es un eCommerce de compra en línea enfocado en la venta de dispositivos electrónicos, ofreciendo una experiencia de compra fácil, rápida y segura.

## 🚀 Instalación y Configuración
1. Clona el repositorio en local
2. Abre el proyecto en tu IDE de preferencia y ubicate en el directorio principal **BUY4U_PROJECT**.
3. Aplica las migraciones usando el comando **python manage.py migrate**.
4. Ejecuta el comando **python manage.py runserver**.
5. Registrate usando el sistema de registro de la página para que puedas interactuar con todas las funcionalidad de la página y todo listo😎.

## 📊 Integración con GitHub Project
Este repositorio está configurado para integrarse automáticamente con el GitHub Project "Buy4U". Cuando se crea un nuevo issue o pull request, se añade automáticamente al tablero del proyecto para facilitar la gestión y seguimiento.

### Configuración del GitHub Project
Para que la integración funcione correctamente, es necesario:
1. Crear un Personal Access Token (PAT) con permisos de `project` y `repo`
2. Añadir el token como secret del repositorio con el nombre `ADD_TO_PROJECT_PAT`
3. Actualizar la URL del proyecto en `.github/workflows/add-to-project.yml` si es necesario
