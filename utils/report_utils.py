from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Pruebas Automatizadas', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Autora: Alejandra Nicole Apaza Cori', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf(texto_resultados, capturas, archivo_salida, duracion, fecha_hora, tipo_prueba="Pruebas Combinadas"):
    try:
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_margins(left=20, top=20, right=20)
        
        # Encabezado con tipo de prueba
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Reporte de {tipo_prueba}", ln=True, align="C")
        pdf.ln(8)
        
        # Información básica
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, f"Fecha: {fecha_hora}", ln=True)
        pdf.cell(0, 7, f"Duración total: {duracion} segundos", ln=True)
        pdf.ln(10)
        
        # Procesar resultados
        current_section = None
        pdf.set_font("Arial", size=10)
        
        for linea in texto_resultados.split('\n'):
            if not linea.strip():
                continue
                
            # Detectar secciones
            if "=== Smoke Test Results ===" in linea:
                current_section = "Smoke Test"
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Smoke Test Results", ln=True)
                pdf.set_font("Arial", size=10)
                continue
            elif "=== Integration Test Results ===" in linea:
                current_section = "Integration Test"
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Integration Test Results", ln=True)
                pdf.set_font("Arial", size=10)
                continue
                
            # Formatear líneas de resultados
            if linea.startswith("V "):
                pdf.set_text_color(0, 128, 0)
                pdf.cell(0, 7, f"[{current_section}] {linea[2:]}", ln=True)
            elif linea.startswith("F "):
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 7, f"[{current_section}] {linea[2:]}", ln=True)
            else:
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 7, linea, ln=True)
        
        pdf.ln(15)
        
        # Sección de capturas (si existen)
        if capturas:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Evidencia de Pruebas:", ln=True)
            pdf.ln(5)
            
            for i, captura in enumerate(capturas):
                if os.path.exists(captura):
                    try:
                        # Asegurarse de que haya espacio suficiente
                        if pdf.get_y() > 250:
                            pdf.add_page()
                            
                        # Insertar imagen con tamaño controlado
                        pdf.image(captura, x=20, w=170)
                        pdf.ln(10)
                    except Exception as img_error:
                        pdf.set_text_color(255, 0, 0)
                        pdf.cell(0, 7, f"Error al cargar captura {i+1}: {str(img_error)}", ln=True)
                        pdf.set_text_color(0, 0, 0)
        
        # Guardar PDF
        pdf.output(archivo_salida)
        print(f"PDF generado correctamente en: {archivo_salida}")
        
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        raise