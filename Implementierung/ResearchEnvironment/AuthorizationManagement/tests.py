import unittest
from django.test import Client

class SimpleTest(unittest.TestCase):
    
    def setUp(self):
        self.client = Client()
        self.client.login(username = 'reader',password='leser1leser')

    
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
            
    def test_resource_manager(self):
        self.client.login(user='admin',password="adm1nistrator")
        response = self.client.get('/resource-manager')
        self.assertEqual(response.status_code, 200)

        
        