from django.db import models
from account.models import Cuser,VendorProfile
from product.models import Product
# Create your models here.

class Order(models.Model):
    ORDER_STATUS = [
        ("pending","Pending"),
        ("confirmed","Confirmed"),
        ("shipped","Shipped"),
        ("delivered","Delivered"),
        ("cancelled","Cancelled"),
    ]
    user = models.ForeignKey(Cuser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=ORDER_STATUS,max_length=20)
    address1 = models.CharField(max_length=255,null=True)
    address_line2 = models.CharField(max_length=255,null=True)
    city = models.CharField(max_length=255,null=True)
    state = models.CharField(max_length=255,null=True)
    postal_code = models.CharField(max_length=20,null=True)
    country = models.CharField(max_length=100,default="India")

class VendorOrders(models.Model):
    ORDER_STATUS = [
        ("pending","Pending"),
        ("confirmed","Confirmed"),
        ("shipped","Shipped"),
        ("delivered","Delivered"),
        ("cancelled","Cancelled"),
    ]
    
    ALLOWED_TRANSITIONS = {
            "pending":["confirmed","cancelled"],
            "confirmed":["shipped","cancelled"],
            "shipped":["delivered"],
            "delivered":[],
            "cancelled":[]
        }
    
    def can_transition(self,new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status,[])

    def change_status(self,new_status):
        if not self.can_transition(new_status):
            raise ValueError(f"Cannot change status from {self.status} to {new_status}")
        
        self.status=new_status
        self.save()
        
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUS)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()

class Payment(models.Model):
    PAYMENT_METHOD=[
        ("cod","Cash on Delivery"),
        ("card","Card"),
        ("upi","UPI"),
    ]

    PAYMENT_STATUS=[
        ("pending","Pending"),
        ("success","Success"),
        ("failed","Failed"),
        ]

    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    payment_method=models.CharField(choices=PAYMENT_METHOD,max_length=50)
    transaction_id=models.CharField(max_length=200)
    status=models.CharField(choices=PAYMENT_STATUS,max_length=20)

