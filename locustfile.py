from locust import HttpUser, task, between
from config import TEST_USER, TEST_PASS, NORMAL_USER, NORMAL_PASS, LOGIN_URL, PLANES_URL, RECURSOS_URL

class WebsiteUser(HttpUser):
    wait_time = between(1, 5) 
    
    def on_start(self):
        """Login when the user starts"""
        self.login()
    
    def login(self):
        """Login with test user credentials"""
        response = self.client.post(LOGIN_URL, {
            "email": TEST_USER,
            "password": TEST_PASS
        })
        if response.status_code != 200:
            print(f"Login failed with status code {response.status_code}")
    
    @task(3)
    def view_planes(self):
        """View planes page"""
        self.client.get(PLANES_URL)
    
    @task(2)
    def view_recursos(self):
        """View recursos page"""
        self.client.get(RECURSOS_URL)
    
    @task(1)
    def login_as_normal_user(self):
        """Test login with normal user credentials"""
        self.client.post(LOGIN_URL, {
            "email": NORMAL_USER,
            "password": NORMAL_PASS
        })