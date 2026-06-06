from django.urls import path
from . import views

urlpatterns = [
    path('products/<int:product_id>/', views.InternalProductDetail.as_view(), name='internal-product-detail'),
    path('products/bulk-lookup/', views.InternalProductBulkLookup.as_view(), name='internal-product-bulk-lookup'),
    path('products/<int:product_id>/reserve-stock/', views.InternalProductReserveStock.as_view(), name='internal-product-reserve-stock'),
    path('products/<int:product_id>/release-stock/', views.InternalProductReleaseStock.as_view(), name='internal-product-release-stock'),
    path('courses/<int:course_id>/', views.InternalCourseDetail.as_view(), name='internal-course-detail'),
]
