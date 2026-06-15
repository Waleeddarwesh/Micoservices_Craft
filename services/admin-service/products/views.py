from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.utils.translation import gettext as _

from accounts.models import Follow
from accounts.serializers import AccountProductSerializer
from .filters import ProductFilter
from .models import Category, Collection, MatCategory, Posters, Product
from .permissions import (IsSupplier, SupplierContractProvided,
                          SupplierHasAddress)
from .serializers import (CategorySerializer, CollectionCreateUpdateSerializer,
                          CollectionSerializer, LatestCollectionSerializer,
                          MatCategorySerializer, PostersSerializer,
                          ProductSerializer, TrendingProductSerializer,
                          ProductAutocompleteSerializer,ProductSearchSerializer)
from .tasks import (send_back_in_stock_notifications_task,
                    send_product_creation_notifications_task)
from audit_logs.utils import log_audit_action


class Categories(APIView):
    @method_decorator(cache_page(60 * 60 * 24)) # Cache for 24 hours
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductsByCategory(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['@ProductName', '@Description']

    def get_queryset(self):
        slug = self.kwargs.get("Slug")
        try:
            category = Category.objects.get(Slug=slug)
            return category.CatPro.select_related('Supplier', 'Category', 'MatCategory').prefetch_related('images', 'Colors', 'Sizes').filter(OutOfStock=False)
        except Category.DoesNotExist:
            return Product.objects.none()
        
    @method_decorator(cache_page(60 * 15)) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(Stock__gt=0).select_related('Supplier', 'Category').prefetch_related('images')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['@ProductName', '@ProductDescription']
    filterset_class = ProductFilter
    ordering_fields = ['UnitPrice']
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsSupplier, SupplierContractProvided, SupplierHasAddress]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('search'):
            return ProductSearchSerializer
        if self.action == 'retrieve':
            return ProductSerializer
        return self.serializer_class
    
    @method_decorator(cache_page(60 * 15)) 
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = request.query_params.get('search', '').strip()
        if len(query) < 3:
            return Response([])

        vector = SearchVector('ProductName', weight='A') + SearchVector('ProductDescription', weight='B')
        query_obj = SearchQuery(query)
        products = Product.objects.annotate(
            rank=SearchRank(vector, query_obj)
        ).filter(rank__gte=0.05).order_by('-rank').only('id', 'ProductName', 'UnitPrice')[:10]
        
        serializer = ProductAutocompleteSerializer(products, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        if not getattr(self.request.user, 'is_supplier', False):
            raise ValidationError(_("Only Suppliers can create products."))

        supplier_instance = self.request.user.supplier
        product = serializer.save(Supplier=supplier_instance)

        # Offload notification sending to Celery
        send_product_creation_notifications_task.delay(supplier_instance.id, product.id)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_stock = instance.Stock
        old_price = instance.UnitPrice

        if not getattr(self.request.user, 'is_supplier', False) or instance.Supplier != self.request.user.supplier:
            raise ValidationError(_("You are not allowed to update this product."))

        product = serializer.save()
        new_stock = product.Stock
        new_price = product.UnitPrice

        if old_price != new_price:
            log_audit_action(
                user=self.request.user,
                action="Supplier changed product price",
                instance=product,
                old_value={'UnitPrice': str(old_price)},
                new_value={'UnitPrice': str(new_price)},
                request=self.request
            )

        # Offload back-in-stock notifications to Celery
        if old_stock == 0 and new_stock > 0:
            send_back_in_stock_notifications_task.delay(product.id)

    def perform_destroy(self, instance):
        if not getattr(self.request.user, 'is_supplier', False) or instance.Supplier != self.request.user.supplier:
            raise ValidationError(_("You are not allowed to delete this product."))
        instance.delete()


class SupplierProductsViewSet(viewsets.ModelViewSet):
    serializer_class = AccountProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'supplier'):
            return Product.objects.select_related(
                'Supplier', 'Category'
            ).prefetch_related('images').filter(
                Supplier=self.request.user.supplier
            )
        return Product.objects.none()


class FollowedSuppliersProducts(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": _("Not authorized")}, status=status.HTTP_401_UNAUTHORIZED)

        follower_instance = None
        if hasattr(request.user, 'customer'):
            follower_instance = request.user.customer
        elif hasattr(request.user, 'supplier'):
            follower_instance = request.user.supplier
        else:
            return Response({"error": _("User must be a customer or supplier")}, status=status.HTTP_400_BAD_REQUEST)

        follower_content_type = ContentType.objects.get_for_model(follower_instance)
        followed_suppliers = Follow.objects.filter(
            follower_content_type=follower_content_type,
            follower_object_id=follower_instance.id
        ).values_list('supplier', flat=True)

        products = Product.objects.select_related(
            'Supplier', 'Category'
        ).prefetch_related('images').filter(
            Supplier__in=followed_suppliers
        ).order_by('-Publish_Date')[:10]
        serializer = TrendingProductSerializer(products, many=True)
        return Response(serializer.data)


class Mataterials(APIView):
    @method_decorator(cache_page(60 * 60 * 24)) # Cache for 24 hours
    def get(self, request):
        materials = MatCategory.objects.all()
        serializer = MatCategorySerializer(materials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsByMaterials(ListAPIView):
    serializer_class = AccountProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['@ProductName', '@ProductDescription']
    ordering_fields = ['UnitPrice']

    def get_queryset(self):
        slug = self.kwargs.get("Slug")
        try:
            material = MatCategory.objects.get(Slug=slug)
            queryset = material.MatCatPro.select_related('Supplier', 'Category', 'MatCategory').prefetch_related('images').filter(OutOfStock=False)
            if hasattr(self.request.user, 'supplier'):
                queryset = queryset.exclude(Supplier=self.request.user.supplier)
            return queryset
        except MatCategory.DoesNotExist:
            return Product.objects.none()


class PostersListAPIView(generics.ListAPIView):
    queryset = Posters.objects.all()
    serializer_class = PostersSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    permission_classes = [IsSupplier]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CollectionCreateUpdateSerializer
        return CollectionSerializer

    def perform_create(self, serializer):
        serializer.save(supplier=self.request.user.supplier)

    def get_queryset(self):
        if hasattr(self.request.user, 'supplier'):
            return self.queryset.filter(supplier=self.request.user.supplier)
        return Collection.objects.none()

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to delete the collection only if the supplier
        who created it is making the request.
        """
        collection = self.get_object()
        if collection.supplier != request.user.supplier:
            return Response({"error": _("You are not authorized to delete this collection.")}, status=status.HTTP_403_FORBIDDEN)
        collection.delete()
        return Response({"message": _("Collection deleted successfully.")}, status=status.HTTP_204_NO_CONTENT)


class CollectionDetailView(APIView):
    def get(self, request, collection_id):
        try:
            collection = Collection.objects.prefetch_related('items__product').get(id=collection_id)
            serializer = CollectionSerializer(collection, context={'request': request, 'view': self})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Collection.DoesNotExist:
            return Response({"error": _("Collection not found")}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestFollowedSuppliersCollections(APIView):
    @method_decorator(cache_page(60 * 30))
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": _("Not authorized")}, status=status.HTTP_401_UNAUTHORIZED)
        
        follower_instance = None
        if hasattr(request.user, 'customer'):
            follower_instance = request.user.customer
        elif hasattr(request.user, 'supplier'):
            follower_instance = request.user.supplier
        else:
            return Response({"error": _("User must be a customer or supplier")}, status=status.HTTP_400_BAD_REQUEST)
        
        follower_content_type = ContentType.objects.get_for_model(follower_instance)
        followed_supplier_ids = Follow.objects.filter(
            follower_content_type=follower_content_type,
            follower_object_id=follower_instance.id
        ).values_list('supplier_id', flat=True)

        collections = Collection.objects.select_related(
            'supplier__user'
        ).prefetch_related(
            'items__product__images'
        ).filter(
            supplier__id__in=followed_supplier_ids
        ).order_by('-created_at')[:10]

        serializer = LatestCollectionSerializer(collections, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)