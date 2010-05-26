from django.db import models
from django.db.models import Model 

class WaitingList(Model):
    email = models.EmailField(max_length=80)
