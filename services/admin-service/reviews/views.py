from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.filters import SearchFilter
from django.db.models import Q
from .models import Review
from .serializers import ReviewSerializer
from accounts.permissions import IsAuthenticated
from products.models import Product
from course.models import Course
from accounts.models import Delivery, Supplier
from products.views import StandardResultsSetPagination

class ReviewCreateView(generics.CreateAPIView):
    """
    API view for creating a new review.
    Handles creation for products, courses, deliveries, and suppliers.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific review.
    A user can only update or delete their own review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            instance = super().get_object()
        except Review.DoesNotExist:
            raise NotFound({"detail": _("Review not found.")})
        
        # Check if the current user owns the review
        if instance.customer.user != self.request.user:
            raise PermissionDenied(_("You do not have permission to perform this action."))
        
        return instance

class ReviewListView(generics.ListAPIView):
    """
    API view to list reviews for a specific object (product, course, etc.).
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['comment']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Review.objects.none()
        product_id = self.kwargs.get('product_id')
        course_id = self.kwargs.get('course_id')
        delivery_id = self.kwargs.get('delivery_id')
        supplier_id = self.kwargs.get('supplier_id')

        if product_id:
            if not Product.objects.filter(id=product_id).exists():
                raise NotFound({"detail": _("Product not found.")})
            queryset = Review.objects.filter(product_id=product_id).filter(Q(status=Review.Status.APPROVED) | Q(customer__user=self.request.user))
            if not queryset.exists():
                raise NotFound({"detail": _("No reviews found for this product.")})
            return queryset
        
        elif course_id:
            if not Course.objects.filter(CourseID=course_id).exists():
                raise NotFound({"detail": _("Course not found.")})
            queryset = Review.objects.filter(course_id=course_id).filter(Q(status=Review.Status.APPROVED) | Q(customer__user=self.request.user))
            if not queryset.exists():
                raise NotFound({"detail": _("No reviews found for this course.")})
            return queryset

        elif delivery_id:
            if not Delivery.objects.filter(id=delivery_id).exists():
                raise NotFound({"detail": _("Delivery not found.")})
            queryset = Review.objects.filter(delivery_id=delivery_id).filter(Q(status=Review.Status.APPROVED) | Q(customer__user=self.request.user))
            if not queryset.exists():
                raise NotFound({"detail": _("No reviews found for this delivery.")})
            return queryset
            
        elif supplier_id:
            if not Supplier.objects.filter(id=supplier_id).exists():
                raise NotFound({"detail": _("Supplier not found.")})
            

            products = Product.objects.filter(Supplier_id=supplier_id)
            if not products.exists():
                raise NotFound({"detail": _("No products found for this supplier.")})
            
            queryset = Review.objects.filter(product__in=products).filter(Q(status=Review.Status.APPROVED) | Q(customer__user=self.request.user))
            
            
            supplier_reviews = Review.objects.filter(supplier_id=supplier_id).filter(Q(status=Review.Status.APPROVED) | Q(customer__user=self.request.user))
            queryset = queryset | supplier_reviews 
            
            if not queryset.exists():
                raise NotFound({"detail": _("No reviews found for this supplier.")})
            
            return queryset.distinct() 

        raise NotFound({"detail": _("Invalid review list endpoint.")})