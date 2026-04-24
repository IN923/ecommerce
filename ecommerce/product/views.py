from django.shortcuts import render
from django.http import JsonResponse
from .models import Product,Product_Images
from .serializers import ProductSerializer
from .utils import decode
from django.contrib import messages
import json
# Create your views here.

#rest_framework imports to build api's
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .utils import decode
from .permissions import VendorApproved,IsVendorOwner

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    print("request body=============",request)
    print("session cart=",request.session.clear())  
    products = json.loads(request.body)
    if ['public_id','product_name','product_price','product_quantity']==list(products):
        data={"success":False,"message":"Fields missing"}
        return Response(data,status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=decode(products["public_id"]))
    except Product.DoesNotExist:
        data ={"success":False,"message":"Product not found"}
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    
    if product.stock==0:
        data={"success":False,"message":"Out of stock"}
        return Response(data)
    
    cart_in_product=0
    product_to_remove=None

    if 'product_data' in request.session:
        for prod in range(len(request.session['product_data'])):
            if products['public_id']==request.session['product_data'][prod]['public_id'] and request.session['product_data'][prod]['product_quantity']>=1:
                print("quantity updated")
                quant = request.session['product_data'][prod]['product_quantity']
                request.session['product_data'][prod]['product_quantity']=quant+int(products['product_quantity'])
                cart_in_product=1

            if products['public_id']==request.session['product_data'][prod]['public_id'] and products["product_quantity"]==0:
                product_to_remove=prod
            
            if request.session['product_data'][prod]['product_quantity']==0:
                product_to_remove=prod

            data = {'success':False}

        if product_to_remove or product_to_remove==0:
            del request.session['product_data'][product_to_remove]

        if not cart_in_product:
            print("new product added")
            request.session['product_data'].append(products)
            data={'success':True,"message":"Product added"}
    else:
        print("cart initialized and new product added")
        request.session['product_data']=[products]
        data={'success':True,"message":"Product added"}
    print('my_cart=',request.session['product_data'])
    
    request.session.modified=True  
    return JsonResponse(data)

# def product_desc(request,id):
#     product = Product.objects.filter(pk=id)
#     print(product)
#     if not product.first():
#         return messages.warning(request,"product not found")
#     return render(request,'main/product_desc.html')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_cartpage(request):
    cart = request.session.get('product_data')
    print('cart11111111',cart)
    context={'cart':cart}
    return render(request,'main/cart_page.html',context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_products(request):
    print("hey u??")
    all_products = Product.objects.all()
    print("all products=",all_products)
    serialized_products = ProductSerializer(all_products,many=True)
    print(serialized_products.data)
    return Response(serialized_products.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request,pk):
    if not pk:
        return Response({"success":"False","message":"Product ID is required."},status=400)
    
    pk=decode(pk)

    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({"success":False,"message":"Invalid Product ID."},status=404)
    
    serialized_product = ProductSerializer(product)
    return Response({"success":True,"product":serialized_product.data},status=200)

class Cart(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes=[IsAuthenticated]

    def product_validation(self,data,allow_negative=False):
        print("product received=",data)

        required_fields={'public_id','product_name','product_price','product_quantity'}
        if not required_fields.issubset(data.keys()):
            data={"success":False,"message":"Fields missing"}
            return None,Response(data,status=status.HTTP_400_BAD_REQUEST)

        data['product_quantity']=int(data['product_quantity'])

        try:
            product = Product.objects.get(id=decode(data["public_id"])[0])
        except Product.DoesNotExist:
            data ={"success":False,"message":"Product not found"}
            return None,Response(data,status=status.HTTP_404_NOT_FOUND)

        if not allow_negative and data['product_quantity']<=0:
            return None,Response({"success":False,"message":"Quantity must be > 0"})

        if product.stock==0:
            data={"success":False,"message":"Out of stock"}
            return None,Response(data)

        if data["product_quantity"]>product.stock:
            return None,Response({"success":False,"message":"Not enough stock"})
        
        return product,None

    def post(self,request):
        cart=request.session.get("product_data",[])
        product_found=False
        products = request.data

        product,err=self.product_validation(products)

        if err:
            return err

        for item in cart:
            if item["public_id"]==products["public_id"]:
                product_found=True
                break

        if not product_found:
            cart.append(products)

        request.session["product_data"]=cart
        request.session.modified=True

        return Response({"success": True, "message": "Cart updated"}, status=200)
    
    def get(self,request):
        cart=request.session.get("product_data",[])
        return Response({"success": True,"cart": cart})
    
    def patch(self,request):
        cart=request.session.get("product_data",[])
        product_to_remove=None
        products=request.data
        product,err=self.product_validation(products,allow_negative=True)
        product_found=False

        if err:
            return err

        for index,item in enumerate(cart):
            if item["public_id"]==products["public_id"]:
                new_quantity=item["product_quantity"]+products["product_quantity"]

                if new_quantity>product.stock:
                    return Response({"success":False,"message":"Stock limit exceeded"}) 

                if new_quantity<=0:
                    product_to_remove=index
                    message="product removed"
                else:
                    item["product_quantity"]=new_quantity
                    message="Quantity updated"

                product_found=True
                break

        if product_to_remove!=None:
            cart.pop(product_to_remove)

        if not product_found:
            return Response({"success":False,"message":"product not found"},status=status.HTTP_404_NOT_FOUND)

        request.session["product_data"]=cart
        request.session.modified=True

        return Response({"success": True, "message": message}, status=200)
    
    def delete(self, request):
        cart = request.session.get("product_data", [])
        public_id = request.data.get("public_id")
        product_to_delete=None

        if not public_id:
            return Response({"success": False, "message": "public_id required"}, status=400)

        for index, item in enumerate(cart):
            if item["public_id"] == public_id:
                product_to_delete=index

        if product_to_delete!=None:
            cart.pop(product_to_delete)
            request.session["product_data"] = cart
            request.session.modified = True
            return Response({"success": True, "message": "Product removed"})

        return Response({"success": False, "message": "Product not found"}, status=404)
    
class ProductView(APIView):
    permission_classes = [VendorApproved,IsVendorOwner]

    def post(self,request):
        category = request.data.get('category')
        name = request.data.get("name")
        price = request.data.get("price")
        stock = request.data.get("stock")
        image = request.FILES.get("image")
        
        if not all([category,name,price,stock]):
            return Response({"message":"All fields are required."},status=status.HTTP_400_BAD_REQUEST)
        
        product_categories = [category[0] for category in Product.CATEGORY_CHOICES]
        if category not in product_categories:
            return Response({"message":"Invalid category"},status=status.HTTP_404_NOT_FOUND)
            
        product = ProductSerializer(data=request.data,context={"request":request})
        if product.is_valid():
            print("product addition validated data",product.validated_data)
            product.save()
            if image:
                Product_Images.objects.create(product=product,image=image)

            return Response({"message":"Product created successfully"})

        return Response(product.errors)
            
    def get(self,request):
        # get the product of only specific vendors
        products = Product.objects.all()

        serialized_product = ProductSerializer(products,many=True,context={"request":request})
        
        return Response({"products":serialized_product.data})
    
    def patch(self,request):
        public_id = request.data.get("public_id")
        category = request.data.get("category")
        name = request.data.get("name")
        stock = request.data.get("stock")
        price = request.data.get("price")
        
        try:
            product = Product.objects.get(id=public_id)
        except Product.DoesNotExist:
            return Response({"message":"Product not found"})
        
        self.check_object_permissions(request,product)

        serializer = ProductSerializer(product,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Product updated"})
        
        return Response({"message":serializer.errors})
        
    def delete(self,request):
        public_id = request.data.get("public_id")

        try:
            product = Product.objects.get(id=public_id)
        except Product.DoesNotExist:
            return Response({"message":"Product not found"})
        
        self.check_object_permissions(request,product)
        
        product.delete()

        return Response({"message":"Product deleted"})
    
class AdminProductList(APIView):
    def get(self,request):
        all_products = Product.objects.all()
        serialized_products = ProductSerializer(all_products)
        return Response(serialized_products.data)
       





            
        
            

            

    


