from django.contrib import admin
from django import forms
from itertools import chain
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory, MoveNodeForm
from .models import StaticPage, MenuType, MenuItem


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'url')


@admin.register(MenuType)
class MenuTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'name')


class ContentTypeSelect(forms.Select):
    def __init__(self, lookup_id, attrs=None, choices=()):
        self.lookup_id = lookup_id
        super(ContentTypeSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)

        choices = chain(self.choices, choices)
        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)
        for choice in choices:
            try:
                ctype = ContentType.objects.get(pk=int(choice[0]))
                choiceoutput += '    \'%s\' : \'../../../%s/%s/?_to_field=%s\',' % (
                    str(choice[0]), ctype.app_label, ctype.model, ctype.model_class()._meta.pk.name)
            except:
                pass
        choiceoutput += '};'

        output += ('<script type="text/javascript">'
                   '(function($) {'
                   '  $(document).ready( function() {'
                   '%(choiceoutput)s'
                   '    $(\'#%(id)s\').change(function (){'
                   '        $(\'#%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]);'
                   '    });'
                   '  });'
                   '})(django.jQuery);'
                   '</script>' % {'choiceoutput': choiceoutput,
                                  'id': attrs['id'],
                                  'fk_id': self.lookup_id
                                  })
        return mark_safe(u''.join(output))


class MenuItemForm(MoveNodeForm):
    class Meta:
        model = MenuItem
        exclude = []

    def __init__(self, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)
        try:
            model = self.instance.content_type.model_class()
            model_key = model._meta.pk.name
        except:
            model = StaticPage
            model_key = 'id'
        self.fields['object_pk'].widget = ForeignKeyRawIdWidget(rel=ManyToOneRel('object_pk', model, model_key), admin_site=admin.site)
        self.fields['content_type'].widget.widget = ContentTypeSelect(
            'lookup_id_object_pk',
            self.fields['content_type'].widget.widget.attrs,
            self.fields['content_type'].widget.widget.choices)

    def clean(self):
        if self.cleaned_data.get('content_type') and self.cleaned_data.get('custom_url'):
            raise forms.ValidationError('You cannot fill both conten type and custom url')
        return self.cleaned_data

    def clean_key(self):
        val = self.cleaned_data.get('key')
        if val and MenuItem.objects.filter(key=val).exists():
            raise forms.ValidationError('This key is already used')
        return val


@admin.register(MenuItem)
class MenuItemAdmin(TreeAdmin):
    list_display = ('id', '__unicode__', 'content_object', 'custom_url', 'active', 'nofollow')
    list_editable = ['active']
    # raw_id_fields = ('menu_type',)
    form = movenodeform_factory(MenuItem, form=MenuItemForm)
    # form = MenuItemForm
    # fieldsets = ((None, {'fields': (('menu_type', 'label', 'key'), ('static_page', 'custom_url'),
    #                                ('active', 'nofollow'))}),)
