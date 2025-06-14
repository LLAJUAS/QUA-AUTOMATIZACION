from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from config import BASE_URL
import os
import time
import requests

class RecursosPage(BasePage):
    # Localizadores
    TARJETA_RECURSO = (By.CSS_SELECTOR, ".card")
    DESCARGAR_BTN = (By.XPATH, ".//a[contains(text(), 'Descargar')]")
    DROPDOWN_ACCIONES = (By.CSS_SELECTOR, ".dropdown-toggle")
    DROPDOWN_MENU = (By.CSS_SELECTOR, ".dropdown-menu")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def load(self):
        self.driver.get(f"{BASE_URL}/recursosenfolders")
        self.wait_for_element(self.TARJETA_RECURSO)
        return self
    
    def get_first_downloadable_resource(self):
        """Encuentra el primer recurso descargable"""
        try:
            recursos = self.find_elements(self.TARJETA_RECURSO)
            for recurso in recursos:
                try:
                    # Abrir el dropdown de acciones
                    dropdown = recurso.find_element(*self.DROPDOWN_ACCIONES)
                    dropdown.click()
                    
                    # Esperar a que aparezca el menú
                    time.sleep(1)  # Pequeña espera para la animación
                    
                    # Encontrar el enlace de descarga
                    download_link = recurso.find_element(*self.DESCARGAR_BTN)
                    return download_link.get_attribute("href")
                except:
                    continue
            return None
        except Exception as e:
            print(f"Error al buscar recursos descargables: {str(e)}")
            return None
    
    def download_file(self, url):
        """Descarga un archivo usando requests con las cookies de la sesión"""
        try:
            # Configurar sesión con cookies del navegador
            session = requests.Session()
            
            # Transferir cookies de Selenium a requests
            selenium_cookies = self.driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Obtener el nombre del archivo de la URL
            filename = os.path.basename(url.split('?')[0])
            local_path = os.path.join(self.download_dir, filename)
            
            # Descargar el archivo
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            # Guardar el archivo
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return local_path
        except Exception as e:
            print(f"Error en la descarga: {str(e)}")
            return None
    
    def download_first_resource(self):
        """Descarga el primer recurso disponible"""
        file_url = self.get_first_downloadable_resource()
        if file_url:
            return self.download_file(file_url)
        return None
    
    def is_file_downloaded(self, filepath, timeout=10):
        """Verifica si el archivo se descargó correctamente"""
        end_time = time.time() + timeout
        while not os.path.exists(filepath):
            time.sleep(1)
            if time.time() > end_time:
                return False
        
        # Verificar que el archivo no esté vacío
        if os.path.getsize(filepath) == 0:
            return False
        
        return True