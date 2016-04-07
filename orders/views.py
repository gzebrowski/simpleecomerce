from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer


class CreateOrderView(APIView):
    def post(self, request, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'OK'})
        else:
            return Response({'status': 'failed'})
