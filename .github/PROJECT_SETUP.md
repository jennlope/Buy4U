# Configuración de la Integración con GitHub Project

Este documento explica cómo configurar la integración automática entre el repositorio Buy4U y el GitHub Project "Buy4U".

## ¿Qué hace esta integración?

La integración automáticamente añade todos los nuevos issues y pull requests al tablero del proyecto Buy4U, facilitando la gestión y seguimiento del trabajo.

## Requisitos Previos

1. Tener un GitHub Project creado (puede ser un proyecto de usuario o de organización)
2. Permisos de administrador en el repositorio

## Pasos de Configuración

### 1. Crear un Personal Access Token (PAT)

1. Ve a GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - URL directa: https://github.com/settings/tokens
2. Haz clic en "Generate new token" → "Generate new token (classic)"
3. Dale un nombre descriptivo, por ejemplo: "Buy4U Project Integration"
4. Selecciona los siguientes permisos:
   - `repo` (Full control of private repositories)
   - `project` (Full control of projects)
5. Haz clic en "Generate token"
6. **¡IMPORTANTE!** Copia el token inmediatamente (no podrás verlo después)

### 2. Añadir el Token como Secret del Repositorio

1. Ve a la configuración del repositorio Buy4U
   - URL: https://github.com/jalopezg4/Buy4U/settings/secrets/actions
2. Haz clic en "New repository secret"
3. Nombre: `ADD_TO_PROJECT_PAT`
4. Valor: Pega el token que copiaste en el paso anterior
5. Haz clic en "Add secret"

### 3. Verificar la URL del Proyecto

1. Abre tu GitHub Project
2. La URL debería ser algo como:
   - Para proyectos de usuario: `https://github.com/users/jalopezg4/projects/NUMERO`
   - Para proyectos de organización: `https://github.com/orgs/NOMBRE_ORG/projects/NUMERO`
3. Si la URL en `.github/workflows/add-to-project.yml` no coincide, actualízala:
   ```yaml
   project-url: https://github.com/users/jalopezg4/projects/1
   ```

### 4. Probar la Integración

1. Crea un nuevo issue o pull request
2. Ve a la pestaña "Actions" del repositorio
3. Verifica que el workflow "Add to Buy4U Project" se ejecutó correctamente
4. Comprueba que el issue/PR aparece en el tablero del proyecto

## Solución de Problemas

### El workflow falla con error de autenticación
- Verifica que el token PAT tiene los permisos correctos (`repo` y `project`)
- Asegúrate de que el secret se llama exactamente `ADD_TO_PROJECT_PAT`

### El workflow falla con error "Resource not accessible"
- Verifica que la URL del proyecto es correcta
- Asegúrate de que el token tiene acceso al proyecto
- Si es un proyecto de organización, verifica que el token tiene permisos en la organización

### El workflow no se ejecuta
- Verifica que el workflow está en `.github/workflows/add-to-project.yml`
- Comprueba que el archivo YAML tiene el formato correcto
- Revisa la pestaña "Actions" para ver si hay errores

## Más Información

- [Documentación de GitHub Actions](https://docs.github.com/en/actions)
- [Documentación de GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Action: add-to-project](https://github.com/actions/add-to-project)
