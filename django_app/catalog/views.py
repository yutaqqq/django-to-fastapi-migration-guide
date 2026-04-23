from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateSerializer


# Endpoint 1: List all products (with category JOIN via select_related)
@api_view(["GET"])
def product_list(request):
    """
    List products. Django ORM uses select_related to avoid N+1.
    Migration note: FastAPI equivalent uses SQLAlchemy joinedload().
    """
    products = Product.objects.select_related("category").all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# Endpoint 2: Get product by ID
@api_view(["GET"])
def product_detail(request, pk):
    try:
        product = Product.objects.select_related("category").get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


# Endpoint 3: Create product
@api_view(["POST"])
def product_create(request):
    serializer = ProductCreateSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Endpoint 4: Update product
@api_view(["PUT"])
def product_update(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductCreateSerializer(product, data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Endpoint 5: Categories with product count (complex JOIN + aggregation)
@api_view(["GET"])
def categories_with_product_count(request):
    """
    Complex query: categories annotated with product count.
    Django ORM: Category.objects.annotate(product_count=Count('products'))
    Migration note: SQLAlchemy equivalent uses func.count() with group_by.
    """
    categories = Category.objects.annotate(
        product_count=Count("products")
    ).order_by("name")

    data = [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "product_count": cat.product_count,
        }
        for cat in categories
    ]
    return Response(data)
