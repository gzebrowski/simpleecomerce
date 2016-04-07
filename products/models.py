from __future__ import unicode_literals
import time
from hashlib import sha1
from django.db import models
# from django.utils.translation import ugettext as _
import os
from django.core.files.storage import get_storage_class
from django.conf import settings
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField

file_storage = get_storage_class(settings.FILE_STORAGE)()


def file_parts(filename, instance):
    fnm = os.path.basename(filename)
    base, ext = os.path.splitext(fnm)
    if instance and instance.pk:
        h = 'p_%s' % instance.pk
    else:
        h = sha1("%s %s" % (filename, time.time())).hexdigest()[:6]
    return slugify(base), h, ext


def get_image_path(instance, filename):
    return 'product/%s_%s%s/' % file_parts(filename, instance)


def get_image_path2(instance, filename):
    return 'custom_order/%s_%s%s/' % file_parts(filename, instance)


def get_image_path3(instance, filename):
    return 'users_images/%s_%s%s/' % file_parts(filename, instance)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = RichTextField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        return 'category_view', (), {'slug': self.slug, 'pk': self.pk}


class Product(models.Model):
    image = models.ImageField(upload_to=get_image_path, blank=True,
                              null=True, storage=file_storage)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    category = models.ForeignKey(Category, null=True, blank=True)
    text = RichTextField(blank=True, null=True)
    price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        if self.category:
            return 'product_view', (), {'slug': self.slug, 'pk': self.pk, 'category_path': self.category.slug}
        else:
            return 'product_view2', (), {'slug': self.slug, 'pk': self.pk}


class CustomCake(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=get_image_path2, blank=True,
                              null=True, storage=file_storage)
    user_image = models.ImageField(upload_to=get_image_path3, blank=True,
                                   null=True, storage=file_storage)
    image_scale = models.FloatField(default=1, blank=True)
    image_top = models.IntegerField(default=0, blank=True)
    image_left = models.IntegerField(default=0, blank=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    font_type = models.CharField(max_length=255, blank=True)
    font_size = models.IntegerField(default=12, blank=True)
    font_color = models.CharField(max_length=16, default='#000', blank=True)
    text_top = models.IntegerField(default=0, blank=True)
    text_left = models.IntegerField(default=0, blank=True)
    price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)

    def __unicode__(self):
        return unicode(self.create_time)
