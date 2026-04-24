from rest_framework.permissions import BasePermission

class UserAccessMethods_ForOrder(BasePermission):
    def has_permission(self,request,view):
        print("permissions CustomerAccessMethods")
        # customer_methods = ["POST","GET","PATCH"]
        # vendor_methods = ["GET","PATCH"]

        # if request.method in customer_methods and request.user.role=="customer":
        #     return True
        # elif request.method in vendor_methods and request.user.role=="vendor":
        #     return True
        
        # return False
    
        if request.user.role=="vendor" and request.method=="POST":
            return False
        
        return True
        