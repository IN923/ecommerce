from django.shortcuts import render,get_object_or_404,redirect
from .models import Order,OrderItem,Payment,VendorOrders
from product.models import Product
from django.http import JsonResponse
import razorpay
import json

# drf imports
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer,OrderItemSerializer,VendorOrderItemSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import UserAccessMethods_ForOrder
from .utils import update_customer_order
# Create your views here.

client=razorpay.Client(auth=("rzp_test_STWQgpdqVFP8ME","VqrAfOECJ41tsab79Bp71Vte"))

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def payment_verify(request):
    print(request.body)

    if 'razorpay_signature' in request.POST:
        order_id=request.POST.get('razorpay_order_id')
        payment_id=request.POST.get('razorpay_payment_id')
        signature=request.POST.get('razorpay_signature')

        order=get_object_or_404(Payment,transaction_id=order_id)
        order.status=Payment.PAYMENT_STATUS[1]
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id":order_id,
                "razorpay_payment_id":payment_id,
                "razorpay_signature":signature,
            })
        
            if request.session['product_data']:
                del request.session['product_data']

            return JsonResponse({'success':True})
        except client.errors.SignatureVerificationError:
            return JsonResponse({'success':False})

@api_view(["GET"]) 
@permission_classes([IsAuthenticated]) 
def show_orders(request):
    all_orders = Order.objects.filter(user=5)
    serialized_orders = OrderSerializer(all_orders,many=True)
    return Response({"all_orders":serialized_orders.data},status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def show_orderitems(request,order_id):
    all_orderaitems=OrderItem.objects.filter(user=request.user,order=order_id)
    serialized_orderitems=OrderItemSerializer(all_orderaitems,many=True)
    return Response({"all_orderitems":all_orderaitems})

# class OrderView(APIView):

#     permission_classes = [IsAuthenticated,UserAccessMethods_ForOrder]

#     def get(self,request,*args,**kwargs):
#         print(args,kwargs)
#         if request.user.role=="customer":
#             all_orders = Order.objects.filter(user=request.user)
#             serialized_orders = OrderSerializer(all_orders,many=True)
#             return Response({"all_orders":serialized_orders.data},status=status.HTTP_200_OK)
#         elif request.user.role=="vendor":
#             product_id = kwargs.get("id")
#             print("products id=>",product_id)
            
#             if not product_id:
#                 Response({"message":"Invalid id"})

#             try:
#                 all_orders=OrderItem.objects.filter(product_id).Order_related(Order)
#             except OrderItem.DoesNotExist:
#                 Response({"messaage":"Order"})
#             return Response(status=status.HTTP_200_OK)
    
#     def post(self,request):
#         details = json.loads(request.body)
#         name =details.get('fullname')
#         email=details.get('email')
#         shipping_address =details.get('shipping_address')
#         city = details.get('city')
#         zip_code = details.get('city')
#         phone_no=details.get('phone_no')

#         if not all([name,email,shipping_address,city,zip_code,phone_no]):
#             data = {"success":False,"message":"Please fill all the fields."}
#             return Response(data,status=400)

#         order=Order.objects.create(user=request.user,status=Order.ORDER_STATUS[0],total_price=0)
#         my_cart = request.session['product_data']
#         print("my_cart=",my_cart)
#         total_price=0
#         for product in my_cart:
#             product_item = Product.objects.get(id=product['product_id'])
#             total_price = total_price+product_item.price*product['product_quantity']
#             OrderItem.objects.create(order=order,product=product_item,quantity=product['product_quantity'])

#         order.total_price=total_price
#         payment = Payment.objects.create(order=order,payment_method=Payment.PAYMENT_METHOD[0],status=Payment.PAYMENT_STATUS[0])

#         print("payment to be done=",order.total_price)
#         payment_data = {
#             "amount":int(order.total_price*100),
#             "currency":"INR",
#         }
#         payment_response = client.order.create(data=payment_data)
#         print(payment_response)
#         payment.transaction_id=payment_response['id']

#         if payment_response or payment_response['status']=="failed":
#             return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

#         return Response({'payment_response':payment_response['status'],"amount":payment_response['amount'],"order_id":payment_response['id'],
#                              'razorpay_callback_url':'http://127.0.0.1:8000/order/payment_verify'})

#     def patch(self,request,**kwargs):
#         print("gateway",request.user)
#         if request.user.role=="vendor":
#             order_id = kwargs["id"]

#             if not order_id:
#                 return Response({"message":"Invalid order id"},status=status.HTTP_400_BAD_REQUEST)

#             order = get_object_or_404(Order,id=order_id)
#             serialized_order = OrderSerializer(order,data=request.data,partial=True)

#             if not serialized_order.is_valid():
#                 return Response(serialized_order.errors,status=status.HTTP_400_BAD_REQUEST)
            
#             serialized_order.save()
#             print("olpbb",serialized_order.data)

#             return Response({"message":"Order updated successfully"})
        
#         elif request.role=="customer":
#             order_status = request.data.get("status")

#             if order_status.lower()!="cancelled":
#                 return Response({"message":"You can only cancel your order.other status changes are not allowed."})
            
#             order = get_object_or_404(Order,id=order_id)
#             serialized_order = OrderSerializer(order,data=request.data,partial=True)

#             if not serialized_order.is_valid():
#                 return Response(serialized_order.errors,status=status.HTTP_400_BAD_REQUEST)
            
#             serialized_order.save()
#             print("olpbb",serialized_order.data)

#             return Response({"message":"Order updated successfully"})

class CustomerOrderListCreateView(APIView):
    def post(self,request):
        details = json.loads(request.body)
        name =details.get('fullname')
        email=details.get('email')
        shipping_address =details.get('shipping_address')
        city = details.get('city')
        zip_code = details.get('zip_code')
        phone_no=details.get('phone_no')

        if not all([name,email,shipping_address,city,zip_code,phone_no]):
            data = {"success":False,"message":"Please fill all the fields."}
            return Response(data,status=400)

        order=Order.objects.create(user=request.user,status=Order.ORDER_STATUS[0],total_price=0)
        my_cart = request.session.get("product_data",[])

        if not my_cart:
            return Response({"message":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)
        print("my_cart=",my_cart)
        total_price=0
        for product in my_cart:
            product_item = Product.objects.get(id=product['product_id'])
            total_price = total_price+product_item.price*product['product_quantity']
            OrderItem.objects.create(order=order,product=product_item,quantity=product['product_quantity'])

        order.total_price=total_price
        payment = Payment.objects.create(order=order,payment_method=Payment.PAYMENT_METHOD[0],status=Payment.PAYMENT_STATUS[0])

        print("payment to be done=",order.total_price)
        payment_data = {
            "amount":int(order.total_price*100),
            "currency":"INR",
        }
        payment_response = client.order.create(data=payment_data)
        print(payment_response)
        payment.transaction_id=payment_response['id']

        if not payment_response or payment_response.get("status")=="failed":
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        payment.save()

        return Response({'payment_response':payment_response['status'],"amount":payment_response['amount'],"order_id":payment_response['id'],
                             'razorpay_callback_url':'http://127.0.0.1:8000/order/payment_verify'})
    
    def get(self,request):
        print("requested user",request.user)
        all_orders = Order.objects.filter(user=request.user)
        print(all_orders)
        serialized_all_orders = OrderSerializer(all_orders,many=True)
        return Response({"orders":serialized_all_orders.data},status=status.HTTP_200_OK)
    
class CustomerOrderDetailView(APIView):
    def get(self,request,*args,**kwargs):
        print(self)
        order_id = kwargs.get("id")

        if not order_id:
            return Response({"message":"Invalid id"})
        
        order_items = OrderItem.objects.filter(order=order_id)
        serialized_order_items = OrderItemSerializer(order_items,many=True)
        return Response({"order_items":serialized_order_items.data})
    
class CustomerOrderUpdateView(APIView):
    def patch(self,request,*args,**kwargs):
        order_id = kwargs.get("id")
        status = request.data.get("status")

        if not order_id:
            return Response({"message":"Invalid id"})
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message":"Invalid Order"})
        
        vendor_order = VendorOrders.objects.filter(order=order).values_list("status",flat=True)

        if status!="cancelled":
            return Response({"message":"Only cancellation allowed"},status=status.HTTP_400_BAD_REQUEST)
        # check vendor order status
        if "shipped" in vendor_order:
            return Response({"message":"cann't cancel order"})
        
        serialized_order = OrderSerializer(order,request.data,partial=True)
        if serialized_order.is_valid():
            serialized_order.save()
            VendorOrders.objects.filter(order=order).update(status="cancelled") #fast update multiple objects
            return Response(serialized_order.data)
        
        return Response(serialized_order.errors,status=status.HTTP_400_BAD_REQUEST)
    
class VendorListUpdateView(APIView):
    def get(self,request,*args,**kwargs):
        product_id = kwargs.get("id")
        if not product_id:
            return Response({"message":"Invalid id"})
        
        product = get_object_or_404(Product,id=product_id)
        order_items = OrderItem.objects.filter(product=product)
        serialized_order_items = VendorOrderItemSerializer(order_items,many=True)
        print(serialized_order_items.data)
        return Response(serialized_order_items.data)
    
    def patch(self,request,*args,**kwargs):
        vendor_order_id = kwargs.get("vendor_order_id")
        status = request.data.get("status")
        if not vendor_order_id:
            return Response({"message":"Invalid id"},status=status.HTTP_400_BAD_REQUEST)
        
        if not status:
            return Response({"message":"status is required"},status=status.HTTP_400_BAD_REQUEST)
        
        vendor_order = get_object_or_404(VendorOrders,id=vendor_order_id)
        
        try:
            vendor_order.change_status(status)
        except ValueError as err:
            return Response({"message":str(err)},status=status.HTTP_400_BAD_REQUEST)
       
        serialized_vendor_order = VendorOrderItemSerializer(vendor_order,data=request.data,partial=True)
        if serialized_vendor_order.is_valid():
            serialized_vendor_order.save()
            update_customer_order(vendor_order.order)
            return Response(serialized_vendor_order.data)

        return Response(serialized_vendor_order.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminOrderListView(APIView):
    def get(self,request):
        all_orders = Order.objects.all()
        serializerd_orders = Order.objects.all()
        return Response(serializerd_orders.data,status=status.HTTP_200_OK)

class AdminOrderItems(APIView):
    def get(self,request,**kwargs):
        order_id = kwargs.get("order_id")

        if not order_id:
            return Response({"message":"Invalid order"},status=status.HTTP_400_BAD_REQUEST)

        try:
            order_items = OrderItem.objects.filter(order=order_id)
        except OrderItem.DoesNotExist:
            return Response({"message":"Order not found"},status=status.HTTP_404_NOT_FOUND)

        serialized_order_items = OrderItemSerializer(order_items,many=True)

        return Response(serialized_order_items.data,status=status.HTTP_200_OK)  


        
         


        





        
        


    

