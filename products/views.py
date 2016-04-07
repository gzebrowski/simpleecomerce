from django.views.generic import DetailView
from .models import Category, Product


class CategoryView(DetailView):
    model = Category
    template_name = 'category.html'


class ProductView(DetailView):
    model = Product
    template_name = 'product.html'
