from rest_framework import serializers
from .models import Order,OrderItem
from account.models import Cuser

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.RelatedField(source='Cuser',read_only=True)

    class Meta:
        model=Order
        fields = "__all__"

    def validate_status(self,value):
        instance = self.instance
        
        print("validate_status",instance,instance.status,value)
        if instance.status=="delivered" and value=="cancelled":
            raise serializers.ValidationError("Cann't cancel order")
        
        if instance.status=="cancelled":
            if value=="cancelled":
                raise serializers.ValidationError("Already cancelled")
            raise serializers.ValidationError("Cann't reactivate order")
        
        if instance.status=="pending":
            if value not in ["cancelled","confirmed","shipped","delivered"]:
                raise serializers.ValidationError("")
            
        if instance.status=="confirmed":
            if value not in ["cancelled","shipped","delivered"]:
                raise serializers.ValidationError("")
            
        if instance.status=="shipped":
            if value not in ["cancelled","delivered"]:
                raise serializers.ValidationError("")

        if instance.status=="delivered":
            raise serializers.ValidationError("")
        
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model=OrderItem
        fields = ["product","quantity"]
        exclude = ["order"]

class VendorOrderItemSerializer(serializers.ModelSerializer):
    # order = serializers.SerializerMethodField()
    # def get_order(self,obj):
    #     print("oppopp",obj.order.user.username)
    #     return {"id":obj.order.id,"total_price":obj.order.total_price}
    order_id = serializers.IntegerField(source="order.id")
    user = serializers.CharField(source="order.user")
    created_at = serializers.DateTimeField(source="order.created_at")
    address1 = serializers.CharField(source="order.address1")
    address2 = serializers.CharField(source="order.address_line2")
    city = serializers.CharField(source="order.state")
    state = serializers.CharField(source="order.state")
    postal_code = serializers.CharField(source="order.postal_code")
    country = serializers.CharField(source="order.country")
    class Meta:
        model = OrderItem
        fields = ["order_id","user","created_at","address1","address2","city","state","postal_code","country","product","quantity"]




