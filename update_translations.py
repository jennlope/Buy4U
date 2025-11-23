#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add new English->Spanish translations to django.po
"""

# New translations needed for admin templates converted to English
new_translations = {
    # browsing_history.html
    "Search History (UI)": "Historial de búsqueda (UI)",
    "Back": "Volver",
    "No records": "No hay registros",
    "Search": "Búsqueda",
    "Loading...": "Cargando...",
    "Empty CSV": "CSV vacío",
    "Error loading data:": "Error cargando datos:",
    "Copy table": "Copiar tabla",
    "Search product...": "Buscar producto...",
    
    # manage.html
    "Quick actions": "Acciones rápidas",
    "Most added to cart products": "Productos más añadidos al carrito",
    "Quick access to reports and administrative tools": "Accesos rápidos a reportes y herramientas administrativas",
    "Add product": "Agregar producto",
    "Fill in the data and press": "Rellena los datos y pulsa",
    "Add": "Agregar",
    "Name": "Nombre",
    "Brand": "Marca",
    "Quantity": "Cantidad",
    "Price": "Precio",
    "Recommend": "Recomendar",
    "AI Recommendation:": "Recomendación IA:",
    "Warranty": "Garantía",
    "Type": "Tipo",
    "Description": "Descripción",
    "Image": "Imagen",
    "Download Excel": "Descargar Excel",
    "Download PDF": "Descargar PDF",
    "No image": "Sin imagen",
    "No products available.": "No hay productos disponibles.",
    "Please enter the product name first": "Por favor ingresa el nombre del producto primero",
    "Querying...": "Consultando...",
    "Suggested price:": "Precio sugerido:",
    "Range:": "Rango:",
    "Confidence:": "Confianza:",
    "Error:": "Error:",
    "Error querying recommendation:": "Error al consultar recomendación:",
    
    # rating_stats.html
    "Rating statistics": "Estadísticas de valoraciones",
    "Average, deviation and number of reviews per product.": "Promedio, desviación y número de reseñas por producto.",
    "Show": "Mostrar",
    "Rating summary": "Resumen de valoraciones",
    "Last updated:": "Última actualización:",
    "Product": "Producto",
    "Reviews": "Reseñas",
    "Average rating": "Calificación media",
    "Deviation": "Desviación",
    "Could not load data.": "No se pudieron cargar los datos.",
    "No data to display.": "No hay datos para mostrar.",
    "An error occurred while loading data.": "Se produjo un error al cargar los datos.",
    
    # top_products.html
    "Top products": "Top productos",
    "View the most viewed and most purchased products.": "Visualiza los productos más vistos y más comprados.",
    "Most viewed": "Más vistos",
    "Last 24 hours": "Últimas 24 horas",
    "Most purchased": "Más comprados",
    "Configurable period": "Periodo configurable",
    "No data": "No hay datos",
    "Request error": "Error en la petición",
    
    # report_export.html
    "Detailed Report": "Informe Detallado",
    "Download a PDF summary with key indicators.": "Descarga un resumen PDF con los principales indicadores.",
    "Period": "Periodo",
    "From": "Desde",
    "To": "Hasta",
    "Format": "Formato",
    "Download report": "Descargar informe",
    "Open in new tab": "Abrir en nueva pestaña",
    "Last generation:": "Última generación:",
    "Visits": "Visitas",
    "Purchases": "Compras",
    "Generating...": "Generando...",
    
    # reports.html
    "Administration reports": "Informes de administración",
    "Trends and most relevant products": "Tendencias y productos más relevantes",
    "period": "periodo",
    "Trends": "Tendencias",
    "last": "últimos",
    "Visits, purchases and average rating": "Visitas, compras y calificación media",
    "Could not load chart data.": "No se pudieron cargar los datos del gráfico.",
    "Fetch failed": "Error en la petición",
    "Updated": "Actualizado",
    "Error": "Error",
    
    # most_added_to_cart.html
    "Ranking of most popular products based on number of times added to cart": "Ranking de productos más populares según cantidad de veces añadidos al carrito",
    "Times added": "Veces añadido",
    "Total unique products added:": "Total de productos únicos añadidos:",
    "No data available yet. Products will appear when users add them to cart.": "No hay datos disponibles aún. Los productos aparecerán cuando los usuarios los añadan al carrito.",
}

def update_po_file():
    po_path = r"c:\Users\Usuario\Documents\Personal\EAFIT\SeptimoSemestre\P2\Buy4U\locale\es\LC_MESSAGES\django.po"
    
    # Read existing file
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new translations at the end (before the last empty line)
    new_entries = []
    for english, spanish in new_translations.items():
        # Check if translation already exists
        if f'msgid "{english}"' not in content:
            entry = f'\nmsgid "{english}"\nmsgstr "{spanish}"\n'
            new_entries.append(entry)
    
    if new_entries:
        # Append new entries to the file
        with open(po_path, 'a', encoding='utf-8') as f:
            f.write('\n# Admin template translations\n')
            for entry in new_entries:
                f.write(entry)
        
        print(f"✅ Added {len(new_entries)} new translations to django.po")
    else:
        print("✅ All translations already exist in django.po")

if __name__ == '__main__':
    update_po_file()
