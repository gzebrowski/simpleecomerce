from orders.forms import OrderForm
from django.conf import settings


def global_values(request):
    return {'order_form': OrderForm(), 'USER_IMAGE_RESTRICTIONS': settings.USER_IMAGE_RESTRICTIONS}
