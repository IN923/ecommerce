from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Cuser,VendorProfile

class CustomizedToken(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)
        token["role"] = user.role
        print(user.role)
        return token
    
class CuserSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cuser
        fields = ["first_name","last_name","username","email","phone_number","role","is_active"]

class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=VendorProfile
        fields = ["store_name","store_description","created_at","is_verified"]

class CuserDetail(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    class Meta:
      model=Cuser
      fields = ["first_name","last_name","username","email","phone_number","role","is_active","vendor"]

    def get_vendor(self,obj):
        print(obj)
        if obj.role=="vendor":
            return VendorProfileSerializer(obj.vendor).data
        return None