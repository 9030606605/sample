from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model — handles all CRUD fields."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
