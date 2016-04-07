import datetime
from rest_framework import serializers
from .models import OrderItem, Order
from products.models import Product, CustomCake
from django.contrib.contenttypes.models import ContentType


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('content_type', 'object_pk', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    coll_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    coll_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    # items2 = OrderItemSerializer(many=True)
    items = serializers.CharField()

    class Meta:
        model = Order
        fields = ('email', 'telephone', 'first_name', 'last_name',
                  'company_name', 'city', 'zip_code', 'street',
                  'house_no', 'text', 'collection_point', 'collection_point',
                  'payment_method', 'coll_date', 'coll_time', 'items')

    def create(self, validated_data):
        dct_trans = {'product': Product, 'customcake': CustomCake}
        tmp_items = validated_data.pop('items')
        today = validated_data.pop('coll_date')
        tm = validated_data.pop('coll_time')
        validated_data['collection_time'] = datetime.datetime.combine(today, tm)
        order = Order.objects.create(**validated_data)
        tmp_items = tmp_items.split(';')
        for item in tmp_items:
            item_data = {}
            item = item.split(':')
            md = dct_trans.get(item[0])
            if not md:
                continue
            try:
                obj = md.objects.get(pk=int(item[1]))
            except md.DoesNotExist:
                continue
            # TODO:
            # if not obj.is_avaliable:
            #    continue
            ct = ContentType.objects.get_for_model(md)
            item_data['content_type'] = ct
            item_data['object_pk'] = obj.pk
            item_data['quantity'] = int(item[2])
            OrderItem.objects.create(order=order, **item_data)
        return order
