New-Item -ItemType Directory -Force .github\ISSUE_TEMPLATE | Out-Null
@"
name: Historia de Usuario
description: Crear HU con criterios de aceptación
title: "HU: "
labels: ["feature","hu"]
body:
  - type: textarea
    attributes: { label: Descripción }
  - type: textarea
    attributes: { label: Criterios de aceptación }
  - type: textarea
    attributes: { label: Tareas }
  - type: checkboxes
    attributes:
      label: Checklist
      options:
        - label: Tests actualizados
        - label: CI en verde
"@ | Set-Content -Encoding UTF8 .github\ISSUE_TEMPLATE\hu.md
