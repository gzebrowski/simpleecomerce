from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Order(models.Model):
    COLLECTION_POINT_CHOICES = (
        (1, 'Ophalen Ootmarsumsestraat 352 - Almelo'),
        (2, 'Ophalen Vincent van Goghplein 21 - Almelo'),
        (3, 'Ophalen Hogepad 1/86 (winkelcentrum de Hoge Wal) - Rijssen'),
    )
    COLLECTION_PAYMENT_METHOD = (
        (1, 'Betalen bij afhalen (Betalen met pin mogelijk)'),
        (2, 'iDEAL'),
    )
    order_time = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)
    zip_code = models.CharField(max_length=12, null=True, blank=True)
    street = models.CharField(max_length=32, null=True, blank=True)
    house_no = models.CharField(max_length=8, null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    collection_time = models.DateTimeField()
    collection_point = models.SmallIntegerField(choices=COLLECTION_POINT_CHOICES)
    payment_method = models.SmallIntegerField(choices=COLLECTION_PAYMENT_METHOD)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return "Order at %s" % self.order_time


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    content_type = models.ForeignKey(
        ContentType,
        verbose_name='content type',
        related_name="content_type_set_for_%(class)s")
    object_pk = models.IntegerField('object ID')
    content_object = GenericForeignKey(
        ct_field="content_type", fk_field="object_pk")
    quantity = models.IntegerField(default=1)

    def __unicode__(self):
        return "Order at %s" % self.content_object
