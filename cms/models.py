from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from treebeard.mp_tree import MP_Node


class StaticPage(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.CharField(max_length=255, null=True, blank=True)
    meta_keywords = models.CharField(max_length=255, null=True, blank=True)
    content = RichTextField(blank=True, null=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.title)

    def get_absolute_url(self):
        return self.url


class MenuType(models.Model):
    name = models.CharField(max_length=255, blank=True)
    key = models.SlugField(null=True, blank=True, help_text="used only in templates")
    class_name = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return ("<%s>" % self.key) if self.key else unicode(self.name)


class MenuItem(MP_Node):
    menu_type = models.ForeignKey(MenuType)
    label = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name='content type',
        help_text='Use url to page of this content type',
        limit_choices_to={'model__in': ['category', 'staticpage', 'product']},
        related_name="content_type_set_for_%(class)s")
    object_pk = models.IntegerField('object ID', null=True, blank=True, help_text='Select object of selected content type')
    content_object = GenericForeignKey(
        ct_field="content_type", fk_field="object_pk")

    custom_url = models.CharField(max_length=255, null=True, blank=True, help_text='any url if content type and pbject ID not specified')
    active = models.BooleanField(default=True)
    nofollow = models.BooleanField(default=False, help_text='for seo purposes')
    key = models.SlugField(null=True, blank=True, help_text="used only in templates")

    def __unicode__(self):
        return "%s %s: %s" % ('. . ' * ((self.depth or 1) - 1), (self.menu_type.key or self.menu_type.name) if self.menu_type else '', self.label)

    @property
    def get_url(self):
        if self.custom_url:
            return self.custom_url
        elif self.content_type and self.object_pk:
            obj = self.content_object
            if obj and getattr(obj, 'get_absolute_url', None):
                return obj.get_absolute_url()
        return '#'


class StaticContent(models.Model):
    key = models.SlugField(max_length=32, help_text="used only in templates", null=True)
    name = models.CharField(max_length=64, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.key


class StaticContentParam(models.Model):
    content = models.ForeignKey(StaticContent)
    key = models.CharField(max_length=64, help_text="used only in templates", null=True)
    value = models.TextField(blank=True)

    def __str__(self):
        return "%s/%s" % (self.content, self.key)


class FormattedContent(models.Model):
    key = models.SlugField(max_length=32, help_text="used only in templates", null=True)
    text = RichTextField()

    def __str__(self):
        return "%s" % (self.key,)
