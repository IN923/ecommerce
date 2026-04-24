from rest_framework.permissions import BasePermission
from account.models import VendorProfile
    
class VendorApproved(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        print(user.is_authenticated)
        if not user or not user.is_authenticated:
            return False
        print("hello,kidda",request.user)
        print(user.role)
        if user.role != "vendor":
            return False

        vendor = VendorProfile.objects.filter(user=user).first()

        return vendor is not None and vendor.is_verified
    
class IsVendorOwner(BasePermission):
    def has_object_permission(self,request,view,obj):
        print("fdfdfdf",obj.vendor==request.user)
        return obj.vendor==request.user