"""
reviews/serializers.py — Platform Service
Cross-service imports removed:
  - REMOVED: from accounts.models import Customer, Delivery, Supplier, User
  - REPLACED: reviewer_id (plain int) + reviewer_name (denormalized string)

The reviewer's identity comes from the JWT — no accounts DB lookup.
Product/course names are denormalized snapshots stored on the Review model.
"""
from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review. All cross-service references are plain IDs +
    denormalized name snapshots — no ForeignKeys to external service DBs.
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "user_id",
            "user_name",
            "product_id",
            "product_name",
            "course_id",
            "course_name",
            "rating",
            "comment",
            "status",
            "is_verified_purchase",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "user_name",
            "status",
            "is_verified_purchase",
            "created_at",
        ]

    def validate(self, data):
        """Ensure exactly one of product_id or course_id is set."""
        has_product = bool(data.get("product_id"))
        has_course  = bool(data.get("course_id"))
        if not has_product and not has_course:
            raise serializers.ValidationError(
                "A review must reference either a product_id or a course_id."
            )
        if has_product and has_course:
            raise serializers.ValidationError(
                "A review cannot reference both a product and a course."
            )
        return data
