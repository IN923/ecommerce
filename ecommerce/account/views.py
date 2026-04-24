from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

#rest_framework imports to build api's
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import CustomizedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from .models import Cuser,VendorProfile
from .serializers import CuserSerializer,CuserDetail
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def create_account(request):
    email = request.data.get('email')
    phone_num = request.data.get('phone')
    role = request.data.get("role")
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not all([email,phone_num,password,confirm_password]):
        return Response({"success":False,"message":"Please fill in all fields."})  

    if password!=confirm_password:
        return Response({"success":False,"message":"Password do not match."})
    
    user = Cuser()
    user.username=email

    if Cuser.objects.filter(username=email).exists():
        return Response({"message":"Username already taken. Please choose another."},status=status.HTTP_400_BAD_REQUEST)

    if role:
        role_list = [role[0] for role in Cuser.Role_Choices]
        user.role=role
        if role not in role_list:
            return Response({"message":"Invalid role"},status=status.HTTP_400_BAD_REQUEST)

    user.phone_number=phone_num
    user.set_password(password)
    user.save()

    if role=="vendor":
        VendorProfile.objects.create(user=user)

    return Response({"success":True,"message":"Account created successfully!"})

# @api_view(["POST"])
# @permission_classes([AllowAny])
# def login_view(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     if not all([username,password]):
#         return Response({"success":False,"message":"Please fill in all fields."})  

#     print(username,password)
#     user = authenticate(username=username,password= password)
#     print("uuuuuuuuu",user)
#     if user:
#         login(request,user)
#         print("uuuuuuuuuuuuuuuuuu",request.user)
#         refresh = RefreshToken.for_user(user)
#         print("Access Token:",refresh.access_token)
#         print("Refresh Token:",refresh)
#         print("payload---------",refresh.payload)
#         refresh["role"]=user.role
#         response = Response({"success":True,"message":"Login success!"})
#         response.set_cookie("access_token",refresh.access_token,secure=False)
#         response.set_cookie("refresh_token",refresh,secure=False)
#         # response.delete_cookie("aToken")
#         # response.delete_cookie("Token")                
#         return response
    
#     return Response({"success":False,"message":"Invalid credentials"})


class Custom_TokenView(TokenObtainPairView):
    serializer_class=CustomizedToken

    def post(self, request):
        print("request.data",request.data)
        serializer = self.get_serializer(data=request.data)
        print("hhhhhhhhhhhhhhhhhhh",serializer.initial_data)
        try:
            serializer.is_valid(raise_exception=True)
            print("eeeeeeeeeeeeeeeeee")
            refresh_token = serializer.validated_data["refresh"]
            access_token = serializer.validated_data["access"]
            response = Response({"access_token":access_token},status=status.HTTP_200_OK)
            response.set_cookie("refresh_token",refresh_token)
            response.set_cookie("access_token",access_token)
        except TokenError as e:
            print("ababababbaaaaaaa",e)
            raise InvalidToken(e.args[0]) from e

        return response
    
class AdminUserList(APIView):
    def get(self,request):
        all_users = Cuser.objects.all()
        serialized_all_users = CuserSerializer(all_users,many=True)

        return Response(serialized_all_users.data)
    
class AdminUserUpdate(APIView):
    def patch(self,request,**kwargs):
        user_id = kwargs.get("user_id")
        is_active = request.data.get("active_status")

        if user_id is None:
            return Response({"message":"Invalid user id"},status=status.HTTP_400_BAD_REQUEST)
        
        if is_active is None:
            return Response({"message":"active status is required"},status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(Cuser,id=user_id)
        serialized_user = CuserSerializer(user,data={"is_active":is_active},partial=True)

        if serialized_user.is_valid():
            serialized_user.save()
            return Response(serialized_user.data,status=status.HTTP_200_OK)
        
        return Response(serialized_user.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminUserDetail(APIView):
    def get(self,request,**kwargs):
        user_id = kwargs.get("id")
        # vendor approve different api_view
        # different serializer for listing user and user detail serializer or different serializer
        if not id:
            return Response({"message":"Invalid user"},status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(Cuser,id=user_id)
        serialized_user = CuserDetail(user)
        return Response(serialized_user.data,status=status.HTTP_200_OK)
    
class VendorApproveView(APIView):
    def patch(self,request,**kwargs):
        user_id=kwargs.get("id")
        is_verified = request.data.get("is_verified")

        if not user_id:
            return Response({"message":"Invalid user id"},status=status.HTTP_400_BAD_REQUEST)
        
        if is_verified is None:
            return Response({"message":"invalid"})

        try:
            user = Cuser.objects.get(id=user_id)
        except Cuser.DoesNotExist:
            return Response({"message":"User not found"},status=status.HTTP_404_NOT_FOUND)
        
        serialized_vendor = CuserDetail(user,data={"is_verified":is_verified},partial=True)
        if serialized_vendor.is_valid():
            serialized_vendor.save()
            return Response(serialized_vendor.data)

        return Response(serialized_vendor.errors)
    


        




         




    




    

    
    



    
    
