from selenium.webdriver.common.by import By
from .base_page import BasePage
from config import PLANES_URL  # Añade esta importación

class PlanesPage(BasePage):
    NOMBRE_PLAN = (By.NAME, "nombre_plan")
    TIPO_PLAN = (By.NAME, "tipo")
    DESCRIPCION = (By.NAME, "descripcion")
    ES_ESTATICO = (By.CSS_SELECTOR, "input[name='es_estatico'][type='checkbox']")
    GUARDAR_BTN = (By.XPATH, "//button[contains(text(), 'Guardar Plan')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def load(self):
        self.driver.get(PLANES_URL)
        return self
    
    def fill_form(self, nombre="Plan Premium Test", tipo="Anual", descripcion="Plan de prueba creado por Selenium", es_estatico=True):
        self.type_text(self.NOMBRE_PLAN, nombre)
        self.type_text(self.TIPO_PLAN, tipo)
        self.type_text(self.DESCRIPCION, descripcion)
        
        if es_estatico:
            checkbox = self.find(self.ES_ESTATICO)
            if not checkbox.is_selected():
                checkbox.click()
        
        return self
    
    def submit_form(self):
        self.click(self.GUARDAR_BTN)
        return self