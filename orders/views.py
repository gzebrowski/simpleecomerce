import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .serializers import OrderSerializer
from utils.emails import sendmail

trans = {'.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png'}


class CreateOrderView(APIView):
    def post(self, request, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            attachments = []
            order_items = []
            total = 0
            for orderitem in order.orderitem_set.all():
                obj = orderitem.content_object
                item = {'quantity': orderitem.quantity, 'price': obj.price, 'title': obj.title}
                item_price = obj.price * orderitem.quantity if orderitem.quantity and obj.price else 0
                total += item_price
                item['item_price'] = item_price
                if obj.image:
                    fname, ext = os.path.splitext(str(obj.image))
                    img_data = obj.image.read()
                    item['image'] = obj.image.url
                    image_key = 'itemimage_%s%s' % (orderitem.id, ext)
                    item['image_key'] = image_key
                    content_type = trans.get(ext.lower(), 'image/jpeg')
                    attachments.append((image_key, img_data, content_type))
                order_items.append(item)
            sendmail(settings.ORDER_RECEIVERS, 'new order', template_html='emails/new_order_notif.html',
                     params={'order': order, 'order_items': order_items, 'total': total},
                     attachments=attachments)
            sendmail(order.email, 'order confirmation', template_html='emails/new_order_confirm.html',
                     params={'order': order, 'order_items': order_items, 'total': total},
                     attachments=attachments)
            return Response({'status': 'OK'})
        else:
            return Response({'status': 'failed'})
