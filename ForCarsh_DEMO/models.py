import email
from pyexpat import model
from django.db import models

# Create your models here.
class Member(models.Model):
    email = models.CharField(max_length=20)
    password = models.CharField(max_length=6)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    institute = models.CharField(max_length=20)
