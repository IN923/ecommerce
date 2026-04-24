from django.urls import path
from .views import create_account
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Custom_TokenView,AdminUserList,AdminUserUpdate,AdminUserDetail

urlpatterns = [
    # path('login',login_view,name='login_view'),
    path('create_account',create_account,name='create_account'),
    # path("generate_refresh",generate_refresh,name="generate_refresh"),
    path("login",Custom_TokenView.as_view(),name="login_view"),
    path("refresh",TokenRefreshView.as_view(),name="refresh_view"),
    path("users/", AdminUserList.as_view()),
    path("users/<int:user_id>/", AdminUserUpdate.as_view()),
    path("user_detail/<int:id>",AdminUserDetail.as_view()),
]