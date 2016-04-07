from orders.forms import OrderForm


def global_values(request):
    return {'order_form': OrderForm()}
