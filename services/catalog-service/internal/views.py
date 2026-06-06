from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from products.models import Product
from course.models import Course

class InternalProductDetail(APIView):
    permission_classes = [] # internal network only

    def get(self, request, product_id):
        product = get_object_or_404(Product, ProductID=product_id)
        return Response({
            'ProductID': product.ProductID,
            'ProductName': product.ProductName,
            'UnitPrice': str(product.UnitPrice),
            'Stock': product.Stock,
            'supplier_id': product.supplier_id,
        })

class InternalProductBulkLookup(APIView):
    permission_classes = []

    def post(self, request):
        ids = request.data.get('ids', [])
        products = Product.objects.filter(ProductID__in=ids)
        result = []
        for product in products:
            result.append({
                'ProductID': product.ProductID,
                'ProductName': product.ProductName,
                'UnitPrice': str(product.UnitPrice),
                'Stock': product.Stock,
                'supplier_id': product.supplier_id,
            })
        return Response(result)

class InternalProductReserveStock(APIView):
    permission_classes = []

    def post(self, request, product_id):
        quantity = request.data.get('quantity', 1)
        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            product = get_object_or_404(Product.objects.select_for_update(), ProductID=product_id)
            if product.Stock >= quantity:
                product.Stock -= quantity
                if product.Stock == 0:
                    product.OutOfStock = True
                product.save(update_fields=['Stock', 'OutOfStock'])
                return Response({'status': 'success', 'Stock': product.Stock})
            else:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

class InternalProductReleaseStock(APIView):
    permission_classes = []

    def post(self, request, product_id):
        quantity = request.data.get('quantity', 1)
        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            product = get_object_or_404(Product.objects.select_for_update(), ProductID=product_id)
            product.Stock += quantity
            if product.Stock > 0:
                product.OutOfStock = False
            product.save(update_fields=['Stock', 'OutOfStock'])
            return Response({'status': 'success', 'Stock': product.Stock})

class InternalCourseDetail(APIView):
    permission_classes = []

    def get(self, request, course_id):
        course = get_object_or_404(Course, CourseID=course_id)
        return Response({
            'CourseID': course.CourseID,
            'CourseTitle': course.CourseTitle,
            'Price': str(course.Price),
            'supplier_id': course.supplier_id,
        })
