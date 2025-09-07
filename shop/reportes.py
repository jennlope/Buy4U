from abc import ABC, abstractmethod
from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas


class GeneradorReporte(ABC):
    @abstractmethod
    def generar(self, queryset):
        pass


class ReporteExcel(GeneradorReporte):
    def generar(self, queryset):
        df = pd.DataFrame(list(queryset.values()))
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=reporte.xlsx"
        df.to_excel(response, index=False)
        return response


class ReportePDF(GeneradorReporte):
    def generar(self, queryset):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Reporte de Productos/Ventas")
        y = 760
        for item in queryset:
            p.drawString(100, y, str(item))
            y -= 20
            if y < 100:
                p.showPage()
                y = 800
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")
