from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_time', 'customer_name', 'city', 'street', 'collection_time', 'completed', 'items', 'total_price')
    search_fields = ['company_name', 'first_name', 'last_name']
    list_filter = ['completed']
    inlines = [OrderItemInline]
    date_hierarchy = 'order_time'
    ordering = ('-order_time',)

    def customer_name(self, obj):
        # company_name first_name last_name
        if obj.company_name:
            return obj.company_name
        return ' '.join(filter(None, [obj.first_name, obj.last_name]))

    def items(self, obj):
        return '<a href="%s?order_id=%s">items</a>' % (reverse('admin:orders_orderitem_changelist'), obj.id)
    items.allow_tags = True

    def total_price(self, obj):
        price = 0
        for item in obj.orderitem_set.all():
            co = item.content_object
            if co.price and item.quantity:
                price += co.price * item.quantity
        return price


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'content_type', 'object_pk', 'content_object', 'quantity')
