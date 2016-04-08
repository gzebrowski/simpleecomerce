import os
import datetime
import time
from django.views.generic import DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
# from django.conf import settings
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
                if size[0] < 128 or size[1] < 128:
                    return Response({'status': 'TOO_SMALL', 'size': ("%sx%s" % size), 'minsize': "128x128"})
                if size[0] > 1024 or size[1] > 1024:
                    return Response({'status': 'TOO_BIG', 'size': ("%sx%s" % size), 'maxsize': "1024x1024"})
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
            serializer.save()
            return Response({'status': 'OK'})
        else:
            return Response({'status': 'failed'})
