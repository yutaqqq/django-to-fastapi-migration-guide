from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.product_list, name="product-list"),
    path("products/<int:pk>/", views.product_detail, name="product-detail"),
    path("products/create/", views.product_create, name="product-create"),
    path("products/<int:pk>/update/", views.product_update, name="product-update"),
    path("categories/stats/", views.categories_with_product_count, name="category-stats"),
]
