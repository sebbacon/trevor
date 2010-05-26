# python
import os
import shutil

# django
from django.test import TestCase
from django.conf import settings
from django.core import mail

# app
from whatever.models import CustomUser
from whatever.models import RegistrationProfile

PASSWORD = "test"

class BaseTest(TestCase):
    """Using this in order to have at least a valid user authenticated from
    twitter"""
    def setUp(self):
        super(BaseTest, self).setUp()
        self.user = CustomUser(username="test@mailinator.com",
                               email="test@mailinator.com",
                               is_active=True)
        self.user.is_active = True
        self.user.set_password(PASSWORD)
        self.user.save()
        profile = RegistrationProfile.objects\
                  .create_profile(self.user)
        self.user.is_active = True
        self.user.save()

        self.user2 = CustomUser(username="test2@mailinator.com",
                               email="test2@mailinator.com",
                               is_active=True)
        self.user2.set_password(PASSWORD)
        self.user2.save()
        profile = RegistrationProfile.objects\
                  .create_profile(self.user2)
        self.user2.is_active = True
        self.user2.save()

        self.user3 = CustomUser(username="test3@mailinator.com",
                               email="test3@mailinator.com",
                               is_active=True)
        self.user3.set_password(PASSWORD)
        self.user3.save()
        profile = RegistrationProfile.objects\
                  .create_profile(self.user3)
        self.user3.is_active = True
        self.user3.save()

        mail.outbox = []
        
        settings.MEDIA_ROOT = '/tmp/orangepictestmedia'
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
            


    def _login(self):
        self.client.login(username=self.user.username,
                          password=PASSWORD)

    def tearDown(self):
        super(BaseTest, self).tearDown()
        if os.path.isdir(settings.MEDIA_ROOT):
            assert settings.MEDIA_ROOT.startswith('/tmp')
            shutil.rmtree(settings.MEDIA_ROOT)
            
        

