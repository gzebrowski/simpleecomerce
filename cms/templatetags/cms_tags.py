from django.utils.safestring import mark_safe
from django.template import Library
from cms.models import StaticContent, StaticContentParam, FormattedContent, MenuType, MenuItem
from django.core.urlresolvers import reverse
register = Library()


@register.assignment_tag(takes_context=True)
def static_element(context, key, keys=None):
    return _static_element_common(key, keys=keys)


def _static_element_common(key, keys=None):
    sc, _ = StaticContent.objects.get_or_create(key=key)
    result = {'text': sc.text, 'admin_url': reverse('admin:cms_staticcontent_change', args=[sc.pk])}
    if keys is not None:
        keys = list(map(lambda s: s.strip(), str(keys).split(',')))
        result.update({o.key: o.value for o in sc.staticcontentparam_set.filter(key__in=keys)})
        for k in keys:
            if k not in result.keys():
                StaticContentParam.objects.create(content=sc, key=k)
                result[k] = ''
    return result


@register.simple_tag(takes_context=True)
def static_element_ctx(context, key, keys=None, as_var=None):
    res = _static_element_common(key, keys=keys)
    if as_var:
        context[as_var] = res
    return ''


@register.simple_tag(takes_context=True)
def formated_block(context, key):
    sc, created = FormattedContent.objects.get_or_create(key=key)
    return mark_safe(sc.text)


@register.inclusion_tag('blocks/base_menu.html', takes_context=True)
def render_menu(context, key, extra_class=None, inner='', **kwargs):
    menu, _ = MenuType.objects.get_or_create(key=key)
    menuitems = menu.menuitem_set.filter(active=True).order_by('path')
    annotated_items = MenuItem.get_annotated_list_qs(menuitems)
    extra_attrs = []
    for k, v in kwargs.items():
        if k.startswith('attr_'):
            extra_attrs.append((k[5:], v))
    return {'menu': menu, 'menuitems': menuitems, 'key': key, 'extra_class': extra_class, 'extra_attrs': extra_attrs,
            'inner': inner, 'annotated_items': annotated_items}


@register.assignment_tag(takes_context=True)
def get_menu(context, key):
    menu, _ = MenuType.objects.get_or_create(key=key)
    menuitems = menu.menuitem_set.filter(active=True).order_by('path')
    annotated_items = MenuItem.get_annotated_list_qs(menuitems)
    return {'menu': menu, 'menuitems': menuitems, 'annotated_items': annotated_items}


def add_custom_attr(boundfield, attr, value):
    boundfield.field.widget.attrs.update({attr: value})
    return boundfield


@register.filter
def add_placeholder(boundfield, value=None):
    if value is None:
        value = boundfield.field.label
    boundfield.field.widget.attrs.update({'placeholder': value})
    return boundfield


@register.filter
def ng_model(boundfield, value=None):
    if value is None:
        value = boundfield.field.name
    boundfield.field.widget.attrs.update({'ng-model': value})
    return boundfield


@register.filter
def add_attr(boundfield, value):
    attr, therest = value.split(':', 1)
    boundfield.field.widget.attrs.update({attr: therest})
    return boundfield


@register.filter
def required(boundfield, value=True):
    if value:
        boundfield.field.widget.attrs.update({'required': 'required'})
    else:
        boundfield.field.widget.attrs.pop('required', None)
    return boundfield


@register.filter
def add_class(boundfield, value=None):
    elcls = boundfield.field.widget.attrs.get('class', '')
    elcls = ' '.join(elcls.split() + [value])
    boundfield.field.widget.attrs.update({'class': elcls})
    return boundfield
