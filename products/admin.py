from django.contrib import admin
from .models import Product, Category, CustomCake


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'img', 'name', 'category', 'price')
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ['category']

    def img(self, obj):
        if obj.image:
            return '<img alt="" src="%s" width="80">' % obj.image.url
    img.allow_tags = True
    img.short_description = 'image'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CustomCake)
class CustomCakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'img', 'create_time')

    def img(self, obj):
        if obj.image:
            return '<img alt="" src="%s" width="80">' % obj.image.url
    img.allow_tags = True
    img.short_description = 'image'
