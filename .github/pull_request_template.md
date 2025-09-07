@"
## Resumen
Se implementa la HU6: reseñas de producto.

## Cambios
- Modelo `Review`
- Form `ReviewForm`
- Vista `CreateReviewView` (valida compra)
- Template `product_detail.html` (lista + form)
- Tests

## Criterios de aceptación
- [ ] Solo usuarios que compraron pueden reseñar
- [ ] Una reseña por usuario/producto
- [ ] Reseñas visibles en el detalle

## Evidencia
## Evidencia
### Formulario reseña
<img width="947" height="866" alt="image" src="https://github.com/user-attachments/assets/17986344-a7b4-44bb-a8a7-f6e1ddf1bd43" />

### Reseña guardada
<img width="957" height="802" alt="image" src="https://github.com/user-attachments/assets/048cc5c7-6a5d-4223-9873-b96369e85288" />

### Prueba de que solo hace reseña quien compra
<img width="941" height="815" alt="image" src="https://github.com/user-attachments/assets/a6ce863a-d222-428b-a4f4-c5bdd93bfcab" />
"@ | Set-Content -Encoding UTF8 .github\pull_request_template.md
