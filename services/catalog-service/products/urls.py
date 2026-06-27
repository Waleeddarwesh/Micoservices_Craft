from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import *

router=routers.DefaultRouter()
router.register('products',ProductViewSet)
router.register('collections', CollectionViewSet, basename='collection')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('internal/products/count/', InternalProductCountView.as_view(), name='internal-products-count'),
    path('',include(router.urls)),
]
