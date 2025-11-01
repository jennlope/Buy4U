import os
from typing import Dict
import json
import re

# Intentar importar las diferentes versiones de Gemini SDK
genai = None
genai_client = None
genai_lib = None

try:
    from google import genai as _genai_mod
    genai = _genai_mod
    genai_lib = "google.genai"
except Exception:
    try:
        import google.generativeai as _genai_mod2
        genai = _genai_mod2
        genai_lib = "google.generativeai"
    except Exception:
        genai = None
        genai_lib = None

class GeminiService:
    def __init__(self):
        from django.conf import settings
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada en settings")
        
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"  # o "gemini-2.0-flash-exp" si está disponible
        
        # Configurar según la librería disponible
        if not genai:
            raise ValueError("No se pudo importar google.generativeai. Instala: pip install google-generativeai")
        
        if genai_lib == "google.genai":
            self.client = genai.Client(api_key=self.api_key)
        elif genai_lib == "google.generativeai":
            genai.configure(api_key=self.api_key)
            self.client = genai
        
        self.lib = genai_lib
    
    def _extract_text_from_response(self, resp):
        """Extrae texto de la respuesta según la librería usada"""
        try:
            if self.lib == "google.genai":
                if hasattr(resp, "text") and resp.text:
                    return resp.text
                if hasattr(resp, "message") and getattr(resp.message, "parts", None):
                    parts = resp.message.parts
                    if len(parts) > 0 and getattr(parts[0], "text", None):
                        return parts[0].text
                return str(resp)
            
            elif self.lib == "google.generativeai":
                # Para google.generativeai
                if hasattr(resp, "text"):
                    return resp.text
                if hasattr(resp, "parts"):
                    return "".join(part.text for part in resp.parts if hasattr(part, "text"))
                if isinstance(resp, dict):
                    cands = resp.get("candidates", [])
                    if cands and len(cands) > 0:
                        first = cands[0]
                        if isinstance(first, dict):
                            content = first.get("content", {})
                            if isinstance(content, dict):
                                parts = content.get("parts", [])
                                if parts and len(parts) > 0:
                                    return parts[0].get("text", "")
                return str(resp)
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
            return str(resp)
    
    def _limpiar_json(self, texto: str) -> str:
        """Limpia el texto para extraer JSON válido"""
        # Remover markdown
        texto = texto.replace("```json", "").replace("```", "").strip()
        # Remover asteriscos y numerales
        texto = texto.replace("*", "").replace("#", "")
        return texto
    
    def recomendar_precio(self, nombre_producto: str, marca: str = "", tipo: str = "") -> Dict:
        """Recomienda un precio para un producto"""
        prompt = f"""
        Eres un experto en comercio electrónico de productos electrónicos.
        
        Analiza este producto y recomienda un precio en USD:
        - Nombre: {nombre_producto}
        - Marca: {marca if marca else "No especificada"}
        - Tipo: {tipo if tipo else "No especificado"}
        
        IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown, sin texto extra).
        
        Formato:
        {{
            "precio_recomendado": 999.99,
            "precio_minimo": 899.99,
            "precio_maximo": 1099.99,
            "justificacion": "Breve explicación del precio",
            "confianza": "alta"
        }}
        """
        
        try:
            if self.lib == "google.genai":
                # Usar la nueva API
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                texto = self._extract_text_from_response(response)
            else:
                # Usar la API clásica
                model = self.client.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                texto = self._extract_text_from_response(response)
            
            # Limpiar y extraer JSON
            texto = self._limpiar_json(texto)
            
            # Buscar JSON en el texto
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', texto, re.DOTALL)
            if json_match:
                datos = json.loads(json_match.group())
                
                # Validar campos requeridos
                campos = ['precio_recomendado', 'precio_minimo', 'precio_maximo', 'justificacion', 'confianza']
                if all(campo in datos for campo in campos):
                    return {
                        "success": True,
                        "data": datos
                    }
            
            # Intentar parsear directamente
            try:
                datos = json.loads(texto)
                return {"success": True, "data": datos}
            except:
                return {
                    "success": False,
                    "error": f"No se pudo extraer JSON válido. Respuesta: {texto[:200]}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al consultar Gemini: {str(e)}"
            }
    
    def comparar_productos(self, producto1: Dict, producto2: Dict) -> Dict:
        """Compara dos productos usando IA"""
        prompt = f"""
        Compara estos dos productos electrónicos y dame un análisis detallado:

        PRODUCTO 1:
        - Nombre: {producto1.get('name', 'N/A')}
        - Marca: {producto1.get('brand', 'N/A')}
        - Precio: ${producto1.get('price', 0)}
        - Tipo: {producto1.get('type', 'N/A')}
        - Descripción: {producto1.get('description', 'N/A')}
        - Garantía: {producto1.get('warranty', 'N/A')}
        - Calificación: {producto1.get('avg_rating', 'N/A')} ({producto1.get('reviews_count', 0)} reseñas)

        PRODUCTO 2:
        - Nombre: {producto2.get('name', 'N/A')}
        - Marca: {producto2.get('brand', 'N/A')}
        - Precio: ${producto2.get('price', 0)}
        - Tipo: {producto2.get('type', 'N/A')}
        - Descripción: {producto2.get('description', 'N/A')}
        - Garantía: {producto2.get('warranty', 'N/A')}
        - Calificación: {producto2.get('avg_rating', 'N/A')} ({producto2.get('reviews_count', 0)} reseñas)

        IMPORTANTE: Responde SOLO con un objeto JSON válido (sin markdown, sin texto extra).

        Formato:
        {{
            "resumen": "Comparación en una oración",
            "ventajas_producto1": ["ventaja 1", "ventaja 2", "ventaja 3"],
            "ventajas_producto2": ["ventaja 1", "ventaja 2", "ventaja 3"],
            "mejor_relacion_calidad_precio": "producto1",
            "recomendacion": "Para quién es mejor cada uno",
            "diferencia_precio": 100.0,
            "veredicto": "Conclusión final"
        }}
        
        El campo "mejor_relacion_calidad_precio" debe ser exactamente "producto1" o "producto2".
        """
        
        try:
            if self.lib == "google.genai":
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                texto = self._extract_text_from_response(response)
            else:
                model = self.client.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                texto = self._extract_text_from_response(response)
            
            # Limpiar y extraer JSON
            texto = self._limpiar_json(texto)
            
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', texto, re.DOTALL)
            if json_match:
                datos = json.loads(json_match.group())
                
                # Validar campos
                campos = ['resumen', 'ventajas_producto1', 'ventajas_producto2', 
                         'mejor_relacion_calidad_precio', 'recomendacion', 'veredicto']
                if all(campo in datos for campo in campos):
                    if 'diferencia_precio' not in datos:
                        datos['diferencia_precio'] = abs(
                            float(producto1.get('price', 0)) - float(producto2.get('price', 0))
                        )
                    return {"success": True, "data": datos}
            
            # Intentar parsear directamente
            try:
                datos = json.loads(texto)
                return {"success": True, "data": datos}
            except:
                return {
                    "success": False,
                    "error": f"No se pudo extraer JSON. Respuesta: {texto[:200]}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al comparar: {str(e)}"
            }