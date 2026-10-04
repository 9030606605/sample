from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for Products.

    Provides:
      - GET    /api/products/        → List all products
      - POST   /api/products/        → Create a product
      - GET    /api/products/{id}/   → Retrieve a product
      - PUT    /api/products/{id}/   → Full update a product
      - PATCH  /api/products/{id}/   → Partial update a product
      - DELETE /api/products/{id}/   → Delete a product
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
