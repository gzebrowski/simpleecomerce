import os
import re
import requests
from rest_framework import serializers
from django.conf import settings
from .models import CustomCake, file_storage
from PIL import Image, ImageDraw, ImageFont
from utils.utils import calc_min_width_height
from StringIO import StringIO
from django.core.files import File


class ImageFrame(serializers.Serializer):
    top = serializers.IntegerField()
    left = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    src = serializers.CharField()

    class Meta:
        fields = ('top', 'left', 'src', 'width', 'height')


class CustomCakeSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField()
    viewport_width = serializers.IntegerField()
    viewport_height = serializers.IntegerField()
    label_padding_left = serializers.IntegerField()
    label_padding_top = serializers.IntegerField()
    image_frames = ImageFrame(many=True)

    class Meta:
        model = CustomCake
        fields = ('text', 'font_type', 'font_size', 'font_color', 'image_scale',
                  'text_top', 'text_left', 'image_url', 'viewport_width',
                  'viewport_height', 'image_frames', 'label_padding_top',
                  'label_padding_left')

    def create(self, validated_data):
        image_url = validated_data.pop('image_url')
        _, ext = os.path.splitext(image_url)
        viewport_width = validated_data.pop('viewport_width')
        viewport_height = validated_data.pop('viewport_height')
        label_padding_left = validated_data.pop('label_padding_left', 0)
        label_padding_top = validated_data.pop('label_padding_top', 0)
        image_frames = validated_data.pop('image_frames', [])
        for imgframe in image_frames:
            content = requests.get(imgframe['src']).content
            fpobj = StringIO(content)
            imgframe['img'] = Image.open(fpobj)
            try:
                if imgframe['img'].mode != 'RGBA':
                    imgframe['img'] = imgframe['img'].convert('RGBA')
            except Exception:
                pass
            new_size = calc_min_width_height(imgframe['img'].size, imgframe['width'], imgframe['height'])
            imgframe['img'] = imgframe['img'].resize(new_size, Image.ANTIALIAS)

        if viewport_width < 1 or viewport_height < 1:
            return
        destimg = Image.new("RGBA", (viewport_width, viewport_height), "rgb(255,255,255)")
        destimg.putalpha(1)
        image_scale = validated_data.get('image_scale', 1)  # should be 0.2675
        assert '..' not in image_url
        assert re.search(r'[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9a-fA-F]+\.[a-z0-9A-Z]+$', image_url)
        file1 = file_storage.open(image_url)
        im_orig = Image.open(file1)
        im = im_orig
        im_format = im.format
        im_size = im.size
        try:
            if im.mode != 'RGBA':
                im = im.convert('RGBA')
        except Exception:
            pass
        if int(image_scale * 10.0) / 10 != 1:
            im_size = int(im_size[0] * image_scale), int(im_size[1] * image_scale)
            im = im.resize(im_size, Image.ANTIALIAS)

        destimg.paste(im, ((viewport_width - im_size[0]) / 2, (viewport_height - im_size[1]) / 2))
        font_size = validated_data.get('font_size', 16)
        text_top = validated_data.get('text_top', 0) + label_padding_left
        text_left = validated_data.get('text_left', 0) + label_padding_top
        text = validated_data.get('text')
        if text:
            draw = ImageDraw.Draw(destimg)
            font_path = settings.TTFONTS.get(validated_data.get('font_type', 'arial').lower())
            fnt = ImageFont.truetype(font_path, font_size)
            color = validated_data.get('font_color', '#000')
            rgb = (0, 0, 0)
            if color.startswith('#'):  # this supports both #13a5f7 and #fff formats
                color = color.strip('#')
                step = len(color) / 3
                rgb = tuple([int(color[x * step:x * step + step] * (3 - step), 16) for x in range(3)])
            draw.text((text_left, text_top), text, font=fnt, fill=rgb)
        for imgfrm in image_frames:
            destimg.paste(imgfrm['img'], (imgfrm['left'], imgfrm['top']), imgfrm['img'])
        validated_data['price'] = settings.CUSTOM_CAKE_PRICE
        cake = CustomCake.objects.create(**validated_data)
        fp = StringIO()
        destimg.save(fp, im_format)
        fp.seek(0)
        file1.seek(0)
        cake.image.save('custom_cake%s' % ext, File(fp))
        cake.user_image.save('user_image%s' % ext, File(file1))
        im_orig.close()
        file1.close()
        file_storage.delete(image_url)
        return cake
