import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from utils.report_utils import generar_pdf
from utils.email_utils import enviar_correo
import os
from config import BASE_URL, DESTINO

def smoke_test(mostrar_navegador=False):
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
        # === Smoke Test Results === (encabezado)
        resultados.append("=== Smoke Test Results ===")
        
        # 1. Smoke Test 1 - Carga de página principal
        test_start = time.time()
        test_key = "Smoke Test 1 - La página principal cargó correctamente"
        try:
            driver.get(BASE_URL)
            time.sleep(2)
            
            if "Prodovi" in driver.title:
                resultados.append(f"V {test_key}")
                capturas.append(LoginPage(driver).take_screenshot("captura_home.png"))
            else:
                resultados.append(f"F {test_key} - Título obtenido: {driver.title}")
        except Exception as e:
            resultados.append(f"F {test_key} - Error: {str(e)}")
        tiempos[test_key] = round(time.time() - test_start, 2)
        
        # 2. Smoke Test 2 - Inicio de sesión
        test_start = time.time()
        test_key_page = "Smoke Test 2 - Accedió a la página de login: http://127.0.0.1:8000/login"
        test_key_login = "Smoke Test 2 - Login exitoso con credenciales válidas"
        
        try:
            # 2.1 Acceso a página de login
            login_page = LoginPage(driver).load()
            resultados.append(f"V {test_key_page}")
            tiempos[test_key_page] = round(time.time() - test_start, 2)
            
            # Captura de pantalla del login
            capturas.append(login_page.take_screenshot("captura_login.png"))
            
            # 2.2 Login con credenciales
            login_start = time.time()
            planes_page = login_page.login()
            resultados.append(f"V {test_key_login}")
            tiempos[test_key_login] = round(time.time() - login_start, 2)
            
            # 3. Smoke Test 3 - Redirección post-login
            test_key = "Smoke Test 3 - Redirección exitosa a: http://127.0.0.1:8000/home"
            test_start_inner = time.time()
            try:
                expected_urls = ["http://127.0.0.1:8000/home"]
                current_url = driver.current_url.lower()
                
                if any(url in current_url for url in expected_urls):
                    resultados.append(f"V {test_key}")
                else:
                    resultados.append(f"F {test_key} - URL actual: {driver.current_url}")
                
                # Captura después del login
                capturas.append(planes_page.take_screenshot("captura_post_login.png"))
            except Exception as e:
                resultados.append(f"F {test_key} - Error: {str(e)}")
            tiempos[test_key] = round(time.time() - test_start_inner, 2)
            
        except Exception as e:
            resultados.append(f"F Smoke Test 2 - Error durante el inicio de sesión: {str(e)}")
        
        # 4. Smoke Test 4 - Creación de planes
        test_start = time.time()
        test_key = "Smoke Test 4 - Accedió correctamente a: http://127.0.0.1:8000/planes/create"
        try:
            # Acceder a la página de creación de planes
            planes_page.load()
            resultados.append(f"V {test_key}")
            tiempos[test_key] = round(time.time() - test_start, 2)
            
            # Captura de pantalla inicial
            capturas.append(planes_page.take_screenshot("captura_planes.png"))
            
            # Smoke Test 4.1 - Verificación de elementos del formulario
            elementos_verificar = [
                ("Nombre del plan", planes_page.NOMBRE_PLAN),
                ("Tipo de plan", planes_page.TIPO_PLAN),
                ("Descripción", planes_page.DESCRIPCION),
                ("Es estático (checkbox)", planes_page.ES_ESTATICO),
                ("Botón Guardar", planes_page.GUARDAR_BTN)
            ]
            
            for label, locator in elementos_verificar:
                element_start = time.time()
                subtest_key = f"Smoke Test 4.1 - {label} - Campo '{label}' encontrado."
                try:
                    planes_page.find(locator)
                    resultados.append(f"V {subtest_key}")
                except Exception as e:
                    resultados.append(f"F {subtest_key} - Error: {str(e)}")
                tiempos[subtest_key] = round(time.time() - element_start, 2)
            
            # Smoke Test 4.2 - Envío del formulario
            test_key = "Smoke Test 4.2 - Formulario enviado correctamente. Redirección exitosa."
            form_start = time.time()
            try:
                planes_page.fill_form().submit_form()
                time.sleep(3)
                
                if "planes" in driver.current_url:
                    resultados.append(f"V {test_key}")
                else:
                    resultados.append(f"F {test_key} - URL actual: {driver.current_url}")
                
                # Captura después del envío
                capturas.append(planes_page.take_screenshot("captura_envio_planes.png"))
                
            except Exception as e:
                resultados.append(f"F {test_key} - Error: {str(e)}")
            tiempos[test_key] = round(time.time() - form_start, 2)
                
        except Exception as e:
            resultados.append(f"F Smoke Test 4 - Error durante la prueba de creación de planes: {str(e)}")
            
    except Exception as e:
        resultados.append(f"F Error general durante el smoke test: {str(e)}")
    finally:
        driver.quit()
    
    duracion_total = round(time.time() - start_time_total, 2)
    tiempos["Total"] = duracion_total

    # Generar y enviar reporte
    pdf_filename = f"reporte_smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    generar_pdf("\n".join(resultados), capturas, pdf_filename, duracion_total, fecha_hora, tiempos)
    
    asunto = "Reporte Smoke Test Completo"
    cuerpo = "Este es el reporte completo del smoke test que incluye:\n1. Carga de página principal\n2. Inicio de sesión\n3. Acceso al dashboard\n4. Creación de planes\n\nAdjuntamos el reporte con capturas."
    
    enviar_correo(asunto, cuerpo, pdf_filename, DESTINO)
    
    # Limpiar archivos temporales
    for f in capturas + [pdf_filename]:
        if os.path.exists(f):
            os.remove(f)
    
    return "\n".join(resultados), duracion_total, fecha_hora, tiempos