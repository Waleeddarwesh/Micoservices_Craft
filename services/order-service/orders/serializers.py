"""
orders/serializers.py — Order Service
Removed: AddressSerializer, User imports from accounts.
Address is now an inline dict field (denormalized snapshot).
User identity comes from the JWT via request.user_id (set by middleware).
"""
from rest_framework import serializers

from .models import Order, OrderItem, Cart, CartItems, Wishlist, WishlistItem

# ─── Address ─────────────────────────────────────────────────────────────────
# No longer imported from accounts.serializers.
# An address snapshot is embedded directly in the order payload.

class AddressSnapshotSerializer(serializers.Serializer):
    """Inline, denormalized shipping address — no FK to auth-service DB."""
    street      = serializers.CharField(max_length=255)
    city        = serializers.CharField(max_length=100)
    state       = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country     = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)


# ─── Order Items ──────────────────────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "supplier_id",
            "quantity",
            "price",
            "color",
            "size",
            "created_at",
            "updated_at"
        ]

# ─── Order ────────────────────────────────────────────────────────────────────

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSnapshotSerializer(required=False)

    class Meta:
        model  = Order
        fields = [
            "id",
            "order_number",
            "user_id",
            "address_id",
            "payment_method",
            "total_amount",
            "discount_amount",
            "delivery_fee",
            "final_amount",
            "status",
            "paid",
            "created_at",
            "updated_at",
            "items",
            "shipping_address"
        ]
        read_only_fields = ["id", "order_number", "user_id", "total_amount", "final_amount", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        validated_data.pop("shipping_address", {})
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CartItems
        fields = [
            "id",
            "CartID",
            "product_id",
            "Quantity",
            "Color",
            "Size"
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemsSerializer(many=True, read_only=True)

    class Meta:
        model  = Cart
        fields = ["id", "user_id", "items", "Created_at"]
        read_only_fields = ["id", "user_id", "Created_at"]


# ─── Wishlist ─────────────────────────────────────────────────────────────────

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WishlistItem
        fields = ["id", "product_id"]


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Wishlist
        fields = ["id", "user_id", "items", "Created_at"]
        read_only_fields = ["id", "user_id", "Created_at"]
