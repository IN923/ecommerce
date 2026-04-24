from django.urls import path
from .views import CustomerOrderListCreateView,CustomerOrderDetailView,CustomerOrderUpdateView,VendorListUpdateView
# checkout
urlpatterns=[
    # path('checkout/',checkout,name="checkout"),
    # path('payment_verify/',payment_verify,name="payment_verify"),
    # path("all_orders",show_orders,name="show_orders"),
    # path("all_orderitems/<int:order_id>",show_orderitems,name="show_orderitems"),
    # path("manage_order/<int:id>",OrderView.as_view(),name="manage_order"),

    path("manage_order_customer",CustomerOrderListCreateView.as_view(),name="customer_list_or_create"),
    path("manage_corder_detail/<int:id>",CustomerOrderDetailView.as_view()),
    path("manage_corder_update/<int:id>",CustomerOrderDetailView.as_view()),
    path("manage_vlist_update/<int:id>",VendorListUpdateView.as_view()),
]