import re
from rest_framework import serializers
from .models import CustomCake, file_storage
from PIL import Image, ImageDraw, ImageFont
# from StringIO import StringIO
from utils.utils import *


class CustomCakeSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField()
    viewport_width = serializers.IntegerField()
    viewport_height = serializers.IntegerField()

    class Meta:
        model = CustomCake
        fields = ('text', 'font_type', 'font_size', 'font_color',
                  'text_top', 'text_left', 'image_url')

    def create(self, validated_data):
        image_url = validated_data.pop('image_url')
        viewport_width = validated_data.pop('viewport_width')
        viewport_height = validated_data.pop('viewport_height')
        assert '..' not in image_url
        assert re.search(r'[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9a-fA-F]+\.[a-z0-9A-Z]+$', image_url)
        file1 = file_storage.open(image_url)
        im = Image.open(file1)
        cake = CustomCake.objects.create(**validated_data)
        return cake
