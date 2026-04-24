from django.db import models
from account.models import Cuser
# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('ELECTRONICS','ELECTRONICS'),
        ('FURNITURE','FURNITURE'),
        ('GARDENRING','GARDENRING'),
        ('Home & Kitchen','Home & Kitchen'),
        ('FOOTWEAR','FOOTWEAR')
    ]

    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=6,decimal_places=2)
    stock=models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=25,choices=CATEGORY_CHOICES)
    vendor = models.ForeignKey(Cuser,on_delete=models.CASCADE,null=True,blank=True)
    # def __str__(self):
    #     return self.name

class Product_Images(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images",default="C:\\Users\\Inderjeet Singh\\Downloads\\2922280_27002")


    
    
    

