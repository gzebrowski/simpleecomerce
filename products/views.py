import os
import datetime
import time
from django.views.generic import DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from PIL import Image
from .models import Category, Product, file_storage
from StringIO import StringIO
from hashlib import md5
from .serializers import CustomCakeSerializer


def path_join(*args):
    return os.path.join(*args).replace('\\', '/')


class CategoryView(DetailView):
    model = Category
    template_name = 'category.html'


class ProductView(DetailView):
    model = Product
    template_name = 'product.html'


class UploadFile(APIView):
    def post(self, request, *args, **kwargs):
        cakefile = request.FILES.get('cakefile')
        if cakefile:
            content = cakefile.read()
            fl2 = StringIO(content)
            try:
                im = Image.open(fl2)
                size = im.size
            except Exception:
                return Response({'status': 'IMAGE_ERROR'})
            else:
                restict = settings.USER_IMAGE_RESTRICTIONS
                if size[0] < restict['min_width'] or size[1] < restict['min_height']:
                    return Response({'status': 'TOO_SMALL', 'size': ("%sx%s" % size), 'minsize': "%sx%s" % (
                        restict['min_width'], restict['min_height'])})
                if size[0] > restict['max_width'] or size[1] > restict['max_height']:
                    return Response({'status': 'TOO_BIG', 'size': ("%sx%s" % size), 'maxsize': "%sx%s" % (
                        restict['max_width'], restict['max_height'])})
                fl2.seek(0)
                now = datetime.datetime.now()
                path = now.strftime('%Y/%m/%d')
                filename, ext = os.path.splitext(cakefile.name or '')
                hsh = md5("%s%s" % (filename, time.time())).hexdigest()
                final_path = path_join('usertmpfiles', path, hsh + ext)
                res_path = file_storage.save(final_path, fl2)
                url = file_storage.url(res_path)
                return Response({'status': 'OK', 'file_url': url, 'size': size, 'file_key': res_path})


class CreateCakeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomCakeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = serializer.save()
            except Exception:
                raise
                return Response({'status': 'failed'})
            return Response({'status': 'OK', 'resultImage': obj.image.url if obj.image else None,
                             'key': 'customcake:%s' % obj.id, 'price': obj.price})
        else:
            print serializer._errors, serializer.initial_data
            return Response({'status': 'failed'})
