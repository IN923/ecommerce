from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class Cuser(AbstractUser):
    Role_Choices = [
        ("customer","customer"),
        ("vendor","vendor")
    ]
    
    phone_number = PhoneNumberField(blank=True,null=True)
    role = models.CharField(choices=Role_Choices,max_length=10,default="customer")

    def __str__(self):
        return f"{self.id}-{self.username}"

class VendorProfile(models.Model):
    user = models.OneToOneField(Cuser,on_delete=models.CASCADE,related_name="vendor")
    store_name = models.CharField(max_length=25)
    store_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name
# 9888848795




    
