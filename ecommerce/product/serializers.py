from rest_framework import serializers
from .models import Product
from .utils import encode,decode

class ProductSerializer(serializers.ModelSerializer):
    public_id=serializers.SerializerMethodField()
    
    class Meta:
        model=Product
        fields=['public_id','name','price','category','stock']

    def get_public_id(self,obj):
        return encode(obj.id)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user

        if user.role!="vendor" or user!=instance.vendor:
            data.pop("stock",None)

        return data
    
    def create(self,validated_data):
        vendor=self.context.get("request").user
        validated_data["vendor"]=vendor
        return super().create(validated_data)
    
    
    
