import unittest
from django.test import Client
from django.test import TestCase
from unittest import skip
from django.contrib.auth.models import User

from AuthorizationManagement.models import *
from test.support import resource

def setUpUsers():
    test_admin = User.objects.create(username='admin')
    test_admin.set_password('123456') 
    test_admin.is_staff = True
    test_admin.is_admin = True
    test_admin.save()
        
    test_user = User.objects.create(username='boncho') 
    test_user.set_password('123456') 
    test_user.save()
    
    test_user2 = User.objects.create(username='evlogi') 
    test_user2.set_password('123456') 
    test_user2.save()
    
    return {'test_admin':test_admin,'test_user':test_user,'test_user2':test_user2}


def setUpResourceAndRequests(users):
    res = Resource.objects.create(name='res',type='text',description='desc',link='res.txt')
    res.readers.add(users['test_user'].id)
    res.owners.add(users['test_user'].id)
    res.readers.add(users['test_admin'].id)
    res.owners.add(users['test_admin'].id)
    res.save()
    
    res2 = Resource.objects.create(name='res2',type='text',description='desc',link='res2.txt')
    res2.readers.add(users['test_user'].id)
    res2.owners.add(users['test_user'].id)
    res2.readers.add(users['test_admin'].id)
    res2.owners.add(users['test_admin'].id)
    res2.save()
    
    access_req = AccessRequest.objects.create(sender=users['test_user2'],resource=res)
    access_req.save()
    access_req2 = AccessRequest.objects.create(sender=users['test_user2'],resource=res2)
    access_req2.save()
    
    deletion_req = DeletionRequest.objects.create(sender=users['test_user'],resource=res)
    deletion_req.save()
    deletion_req2 = DeletionRequest.objects.create(sender=users['test_user'],resource=res2)
    deletion_req2.save()

def deleteUsers():
    User.objects.all().delete()
    
def deleteResourcesAndRequests():
    AccessRequest.objects.all().delete()
    DeletionRequest.objects.all().delete()
    Resource.objects.all().delete()

class TestHomeView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setUpUsers()
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/')
        self.assertEqual(str(response.context['user']),'boncho')
        self.assertEqual(response.status_code, 200)   
        
    
        
class TestResourceManager(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setUpUsers()
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/resource-manager/')
        self.assertEqual(response.status_code, 302)
        
    def test_logged_in_no_admin(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resource-manager/')
        self.assertEqual(response.status_code, 302)
    
    def test_normal(self):
        self.client.login(username='admin', password='123456')
        response = self.client.get('/resource-manager/')
        self.assertEqual(str(response.context['user']),'admin')
        self.assertEqual(response.status_code, 200)      
        
class TestUserManager(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setUpUsers()
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/user-manager/')
        self.assertEqual(response.status_code, 302)
        
    def test_logged_in_no_admin(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/user-manager/')
        self.assertEqual(response.status_code, 302)
    
    def test_normal(self):
        self.client.login(username='admin', password='123456')
        response = self.client.get('/user-manager/')
        self.assertEqual(str(response.context['user']),'admin')
        self.assertEqual(response.status_code, 200)
        
        
class TestProfileView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
        
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        
    def test_normal(self):
       
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/')
        self.assertEqual(str(response.context['user']),'boncho')
        self.assertEqual(response.status_code, 200)     
        
    def test_pagination_user(self):
        #User has to see only the two access requests for him
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/')
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == False) 
        self.assertEqual(len(response.context['requests_list']), 2)
        
    def test_pagination_admin_page_1(self):
        #Admin has to see the two access and the two deletion requests for him
        #Only 2 of them are shown on page 1
        self.client.login(username='admin', password='123456')
        response = self.client.get('/profile/')
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['requests_list']), 2)
        
        
    def test_pagination_admin_page_2(self):
        #Admin has to see the two access and the two deletion requests for him
        #The second 2 of them are shown on page 2
        self.client.login(username='admin', password='123456')
        response = self.client.get('/profile/?page=2')
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['requests_list']), 2)
        
class TestMyResourcesView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/profile/my-resources/')
        self.assertEqual(response.status_code, 302)
        
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/')
        self.assertEqual(str(response.context['user']),'boncho')
        self.assertEqual(response.status_code, 200) 
    
    def test_resources_shown(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/')
        self.assertTrue('resource_list' in response.context)
        self.assertEqual(len(response.context['resource_list']), 2)
 
class TestSendAccessRequest(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        res = Resource.objects.create(name='res',type='text',description='desc',link='res.txt')
        res.readers.add(users['test_user'].id)
        res.owners.add(users['test_user'].id)
        res.readers.add(users['test_admin'].id)
        res.owners.add(users['test_admin'].id)
        res.save()
        
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/send-access-request/1')
        self.assertEqual(response.status_code, 302)
    
    def test_staff_user(self):
        self.client.login(username='admin', password='123456')
        response = self.client.post('/send-access-request/1')
        self.assertEqual(response.status_code, 302)
    
    def test_reader(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.post('/send-access-request/1')
        self.assertEqual(response.status_code, 302)
       
    def test_post(self):       
        self.client.login(username='evlogi', password='123456')
        response = self.client.post('/send-access-request/1', {'descr':''})
        self.assertEqual(response.status_code, 302) 
       
class TestCancelAccessRequest(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/cancel-access-request/1')
        self.assertEqual(response.status_code, 302)
    
    def test_staff_user(self):
        self.client.login(username='admin', password='123456')
        response = self.client.post('/cancel-access-request/1')
        self.assertEqual(response.status_code, 302)
    
    def test_reader(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.post('/cancel-access-request/1')
        self.assertEqual(response.status_code, 302)
       
    def test_post(self):       
        self.client.login(username='evlogi', password='123456')
        response = self.client.post('/cancel-access-request/1')
        self.assertEqual(response.status_code, 302)

class TestDeleteResourceView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/delete-resource/1')
        self.assertEqual(response.status_code, 302)
    
    def test_not_staff_user(self):
        self.client.login(username='evlogi', password='123456')
        response = self.client.post('/delete-resource/1')
        self.assertEqual(response.status_code, 403)
        
    def test_post(self):       
        self.client.login(username='admin', password='123456')
        response = self.client.post('/delete-resource/1', {'descr':''})
        self.assertEqual(response.status_code, 302)
    



class TestEditNameView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/profile/edit-name/')
        self.assertEqual(response.status_code, 302)
        
    def test_post(self): 
        self.client.login(username='boncho', password='123456')
        response = self.client.post('/profile/edit-name/', {'firstName':'', 'lastName': ''})
        self.assertEqual(response.status_code, 302)
    

class TestResourcesOverview(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/resources-overview/')
        self.assertEqual(response.status_code, 302)
        
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resources-overview/')
        self.assertEqual(str(response.context['user']),'boncho')
        self.assertEqual(response.status_code, 200) 
    
    def test_pagination_user(self):
        #User has to see only the two resources 
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resources-overview/')
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == False) 
        self.assertEqual(len(response.context['resources_list']), 2)
        
class TestResourcesOverviewSearch(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
    
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/resources-overview/search?q=2')
        self.assertEqual(response.status_code, 302)
         
    
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resources-overview/search?q=2')
        self.assertEqual(response.status_code, 200)
        
    def test_no_query(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resources-overview/search')
        self.assertEqual(response.status_code, 302)
     
    def test_valid_query(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/resources-overview/search?q=2')
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == False) 
        self.assertEqual(len(response.context['resources_list']), 1)
          
class TestPermissionEditingView(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
        
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/profile/my-resources/1-edit-users-permissions')
        self.assertEqual(response.status_code, 302)
        
    def test_not_authorized_user(self):
        self.client.login(username='evlogi', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/')
        self.assertEqual(response.status_code, 403)   
        
    def test_admin(self):      
        self.client.login(username='admin', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/')
        self.assertEqual(response.status_code, 302)   
        
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/')
        self.assertEqual(response.status_code, 200) 
    @skip
    def test_shown_users(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/')
        self.assertTrue('user_list' in response.context)
        #Depending on the future implementation
        self.assertEqual(len(response.context['user_list']), 3)
        
    def test_post_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.post('/profile/my-resources/1-edit-users-permissions/')
        self.assertEqual(response.status_code, 302) 
        
        
class TestPermissionEditingViewSearch(TestCase):
         
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = setUpUsers()
        setUpResourceAndRequests(users)
        
    def setUp(self):
        self.client = Client()
        
    @classmethod
    def tearDownClass(cls):
        deleteResourcesAndRequests()
        deleteUsers()
        super().tearDownClass()

    def test_not_logged_in(self):
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search?q=evl')
        self.assertEqual(response.status_code, 302)
        
    def test_not_authorized_user(self):
        self.client.login(username='evlogi', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search?q=evl')
        self.assertEqual(response.status_code, 403)   
        
    def test_admin(self):      
        self.client.login(username='admin', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search?q=evl')
        self.assertEqual(response.status_code, 302)   
        
    def test_no_query(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search')
        self.assertEqual(response.status_code, 302) 
        
    def test_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search?q=evl')
        self.assertEqual(response.status_code, 200) 
        
    def test_valid_query(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.get('/profile/my-resources/1-edit-users-permissions/search?q=evl')
        self.assertTrue('user_list' in response.context)
        self.assertEqual(len(response.context['user_list']), 1)
        
    def test_post_normal(self):
        self.client.login(username='boncho', password='123456')
        response = self.client.post('/profile/my-resources/1-edit-users-permissions/')
        self.assertEqual(response.status_code, 302) 