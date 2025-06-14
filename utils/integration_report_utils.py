from fpdf import FPDF
from datetime import datetime
import os

class IntegrationPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Reporte de Prueba de Integración', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, 'Automatización: Login + Base de Datos', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_integration_pdf(resultados, capturas, archivo_salida, duracion, fecha_hora):
    try:
        pdf = IntegrationPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_margins(left=20, top=20, right=20)
        
        # Encabezado específico para integración
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Resultados de la Prueba de Integración", ln=True)
        pdf.ln(5)
        
        # Información de la prueba
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"Fecha y hora de ejecución: {fecha_hora}", ln=True)
        pdf.cell(0, 6, f"Duración total: {duracion} segundos", ln=True)
        pdf.ln(10)
        
        # Tabla de resultados
        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 8, "Prueba", border=1)
        pdf.cell(40, 8, "Resultado", border=1)
        pdf.cell(40, 8, "Tiempo", border=1)
        pdf.ln(8)
        
        pdf.set_font("Arial", size=10)
        for linea in resultados.split('\n'):
            if not linea.strip():
                continue
                
            # Formatear líneas de resultados
            if linea.startswith("V "):
                pdf.set_text_color(0, 128, 0)
                pdf.cell(90, 8, linea[2:], border=1)
                pdf.cell(40, 8, "ÉXITO", border=1)
                pdf.cell(40, 8, f"{duracion}s", border=1)
                pdf.ln(8)
            elif linea.startswith("F "):
                pdf.set_text_color(255, 0, 0)
                pdf.cell(90, 8, linea[2:], border=1)
                pdf.cell(40, 8, "FALLO", border=1)
                pdf.cell(40, 8, f"{duracion}s", border=1)
                pdf.ln(8)
            else:
                pdf.set_text_color(0, 0, 0)
                pdf.cell(170, 8, linea, border=1, ln=1)
        
        pdf.ln(15)
        
        # Sección de capturas con título específico
        if capturas:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Evidencia de Integración:", ln=True)
            pdf.ln(5)
            
            for i, captura in enumerate(capturas):
                if os.path.exists(captura):
                    try:
                        # Asegurar espacio para la imagen
                        if pdf.get_y() > 250:
                            pdf.add_page()
                            
                        # Insertar imagen con tamaño controlado
                        pdf.image(captura, x=20, w=170)
                        
                        # Añadir descripción bajo cada captura
                        pdf.set_font("Arial", "I", 8)
                        pdf.cell(0, 5, f"Captura {i+1}: {get_capture_description(i)}", ln=True)
                        pdf.ln(5)
                    except Exception as img_error:
                        pdf.set_text_color(255, 0, 0)
                        pdf.cell(0, 7, f"Error al cargar captura {i+1}: {str(img_error)}", ln=True)
                        pdf.set_text_color(0, 0, 0)
        
        # Guardar PDF
        pdf.output(archivo_salida)
        print(f"Reporte de integración generado en: {archivo_salida}")
        
    except Exception as e:
        print(f"Error al generar PDF de integración: {str(e)}")
        raise

def get_capture_description(index):
    descriptions = [
        "Pantalla de login antes de la autenticación",
        "Pantalla posterior al login exitoso",
        "Consulta a base de datos verificando credenciales"
    ]
    return descriptions[index] if index < len(descriptions) else "Captura de evidencia"