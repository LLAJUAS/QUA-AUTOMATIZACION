from selenium.webdriver.common.by import By
from .base_page import BasePage
from .planes_page import PlanesPage  # Añade esta línea
from config import TEST_USER, TEST_PASS, LOGIN_URL # Añade LOGIN_URL aquí

class LoginPage(BasePage):
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def load(self):
        self.driver.get(LOGIN_URL)
        return self
    
    def login(self, email=TEST_USER, password=TEST_PASS):
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        return PlanesPage(self.driver)