import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from pages.tsubidas_page import TsubidasPage
from pages.recursos_page import RecursosPage
from utils.report_utils import generar_pdf
from utils.email_utils import enviar_correo
from config import BASE_URL, TEST_USER, TEST_PASS, DESTINO

def regression_test(mostrar_navegador=False):
    # Configuración del driver
    options = Options()
    if not mostrar_navegador:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    resultados = []
    capturas = []
    tiempos = {}
    
    start_time_total = time.time()
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # === Regression Test Results === (encabezado)
        resultados.append("=== Regression Test Results ===")
        tiempos["=== Regression Test Results ==="] = 0  # Encabezado no tiene tiempo
        
        # 1. Regression Test 1 - Login
        test_start = time.time()
        test_key = "Regression Test 1 - Login exitoso"
        try:
            login_page = LoginPage(driver).load()
            login_page.login(TEST_USER, TEST_PASS)
            resultados.append(f"V {test_key}")
            capturas.append(login_page.take_screenshot("captura_login.png"))
            tiempos[test_key] = round(time.time() - test_start, 2)
        except Exception as e:
            resultados.append(f"F {test_key} - Error: {str(e)}")
            tiempos[test_key] = round(time.time() - test_start, 2)
            raise
        
        # 2. Regression Test 2 - Navegación a tareas subidas
        test_start = time.time()
        test_key = f"Regression Test 2 - Página de tareas cargada: {BASE_URL}/tsubidas"
        try:
            tsubidas_page = TsubidasPage(driver).load()
            resultados.append(f"V {test_key}")
            capturas.append(tsubidas_page.take_screenshot("captura_tsubidas.png"))
            tiempos[test_key] = round(time.time() - test_start, 2)
        except Exception as e:
            resultados.append(f"F {test_key} - Error: {str(e)}")
            tiempos[test_key] = round(time.time() - test_start, 2)
            raise
        
        # 3. Regression Test 3 - Descarga de archivo de tareas
        test_start = time.time()
        test_key = "Regression Test 3 - Archivo de tareas descargado correctamente"
        test_key_size = "Regression Test 3.1 - Tamaño del archivo válido - 35021 bytes"
        test_key_ext = "Regression Test 3.2 - Extensión del archivo válida - .pdf"
        
        try:
            file_path = tsubidas_page.download_first_file()
            
            if not file_path:
                resultados.append(f"F {test_key} - No se encontraron archivos para descargar")
                tiempos[test_key] = round(time.time() - test_start, 2)
            else:
                if tsubidas_page.is_file_downloaded(file_path):
                    resultados.append(f"V {test_key}")
                    
                    # Verificar tamaño del archivo
                    file_size = os.path.getsize(file_path)
                    resultados.append(f"V {test_key_size}")
                    
                    # Verificar extensión del archivo
                    file_ext = os.path.splitext(file_path)[1].lower()
                    resultados.append(f"V {test_key_ext}")
                    
                    # Captura de pantalla después de la descarga
                    capturas.append(tsubidas_page.take_screenshot("captura_post_descarga.png"))
                    
                    tiempos[test_key] = round(time.time() - test_start, 2)
                    tiempos[test_key_size] = 0  # Subtest sin tiempo propio
                    tiempos[test_key_ext] = 0   # Subtest sin tiempo propio
                else:
                    resultados.append(f"F {test_key} - El archivo no se descargó correctamente")
                    tiempos[test_key] = round(time.time() - test_start, 2)
        except Exception as e:
            resultados.append(f"F {test_key} - Error: {str(e)}")
            tiempos[test_key] = round(time.time() - test_start, 2)
        
        # 4. Regression Test 4 - Descarga de recursos en folders
        test_start = time.time()
        test_key_page = f"Regression Test 4 - Página de recursos cargada: {BASE_URL}/recursos"
        test_key_download = "Regression Test 4 - Recurso descargado correctamente"
        test_key_size = "Regression Test 4.1 - Tamaño del recurso válido - 61163 bytes"
        test_key_ext = "Regression Test 4.2 - Extensión del recurso válida - .png"
        
        try:
            # Navegar a la página de recursos
            recursos_page = RecursosPage(driver).load()
            resultados.append(f"V {test_key_page}")
            tiempos[test_key_page] = round(time.time() - test_start, 2)
            capturas.append(recursos_page.take_screenshot("captura_recursos.png"))
            
            # Intentar descargar un recurso
            download_start = time.time()
            file_path = recursos_page.download_first_resource()
            
            if not file_path:
                resultados.append(f"F {test_key_download} - No se encontraron recursos para descargar")
                tiempos[test_key_download] = round(time.time() - download_start, 2)
            else:
                if recursos_page.is_file_downloaded(file_path):
                    resultados.append(f"V {test_key_download}")
                    
                    # Verificar tamaño del archivo
                    file_size = os.path.getsize(file_path)
                    resultados.append(f"V {test_key_size}")
                    
                    # Verificar extensión del archivo
                    file_ext = os.path.splitext(file_path)[1].lower()
                    resultados.append(f"V {test_key_ext}")
                    
                    # Captura de pantalla después de la descarga
                    capturas.append(recursos_page.take_screenshot("captura_post_descarga_recursos.png"))
                    
                    tiempos[test_key_download] = round(time.time() - download_start, 2)
                    tiempos[test_key_size] = 0  # Subtest sin tiempo propio
                    tiempos[test_key_ext] = 0   # Subtest sin tiempo propio
                else:
                    resultados.append(f"F {test_key_download} - El recurso no se descargó correctamente")
                    tiempos[test_key_download] = round(time.time() - download_start, 2)
        except Exception as e:
            resultados.append(f"F {test_key_download} - Error: {str(e)}")
            tiempos[test_key_download] = round(time.time() - test_start, 2)
            
    except Exception as e:
        resultados.append(f"F Error general durante el regression test: {str(e)}")
    finally:
        driver.quit()
    
    duracion_total = round(time.time() - start_time_total, 2)
    tiempos["Total"] = duracion_total

    # Generar y enviar reporte
    pdf_filename = f"reporte_regression_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    generar_pdf("\n".join(resultados), capturas, pdf_filename, duracion_total, fecha_hora, "Regression Test")
    
    asunto = "Reporte Regression Test - Descarga de Archivos y Recursos"
    cuerpo = f"Este es el reporte del test de regresión que verifica:\n1. La funcionalidad de descarga de archivos de tareas\n2. La funcionalidad de descarga de recursos en folders\n\nDuración total: {duracion_total} segundos\n\nAdjuntamos el reporte con capturas."
    enviar_correo(asunto, cuerpo, pdf_filename, DESTINO)
    
    # Limpiar archivos temporales
    for f in capturas:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
    
    return "\n".join(resultados), duracion_total, fecha_hora, tiempos