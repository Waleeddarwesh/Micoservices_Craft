from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('whishlists', views.WishlistViewSet, basename='whishlist')
router.register('carts', views.CartViewSet, basename='cart')
router.register('orders', views.OrderViewSet, basename="order")

urlpatterns = [
    path('internal/orders/count/', views.InternalOrderCountView.as_view(), name='internal-orders-count'),
    path('', include(router.urls)),
]