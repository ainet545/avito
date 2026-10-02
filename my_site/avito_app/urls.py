from django.contrib.auth import logout
from .views import *
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'review',ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('product/', ProductListAPTView.as_view(),name='product'),
    path('product/<int:pk>',ProductDetailAPTView.as_view(),name='product-detail'),
    path('category/',CategoryListAPTView.as_view(), name='category_list'),
    path('category/<int:pk>/',CategoryDetailAPTView.as_view(), name='category_detail'),
    path('subcategory/', SubCategoryListAPTView.as_view(), name='subcategory_list'),
    path('subcategory/<int:pk>/', SubCategoryDetailAPTView.as_view(), name='subcategory_list'),
    path('user/', UserProfileListAPTView.as_view(),name='user_list'),
    path('user/<int:pk>/', UserProfileUpdateAPTView.as_view(), name='user_detail'),
    path('register/',RegisterView.as_view(),name='user_register'),
    path('login/', CustomLoginView.as_view(), name='user_login'),
    path('logout/',LogoutView.as_view(),name='user_logout'),
    path('cart/', CartAPIView.as_view(), name='cart_detail'),
    path('cart_item/', CartItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cart_item/<int:pk>/', CartItemViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('favorite/', FavoriteAPIView.as_view(), name='favorite_detail'),
    path('favorite_item/', FavoriteItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('favorite_item/<int:pk>', FavoriteItemViewSet.as_view({'delete': 'destroy'}))


]