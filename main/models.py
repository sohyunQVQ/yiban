from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    name = models.CharField(max_length=256,default="")
    blogtext = models.CharField(max_length=50,default="")
    pushtext = models.CharField(max_length=50,default="")
    def __str__(self):
        return self.name