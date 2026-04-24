from django.urls import path
from .views import add_to_cart,show_cartpage,show_all_products,product_detail,Cart,ProductView
# product_desc

urlpatterns = [
    path('add_to_cart',add_to_cart,name='add_to_cart'),
    # path('product_description/<int:id>',product_desc,name="product_desc"),
    path('cart',Cart.as_view(),name='cart'),
    path('all_products',show_all_products,name="get_all_products"),
    path('product/<str:pk>',product_detail,name="product_detail"),
    path("manage_product",ProductView.as_view(),name="manage_product")
]

