import os
from PIL import Image

from StringIO import StringIO
from django.conf import settings
from django.core.files import File
from django.core.files.storage import get_storage_class

storage = get_storage_class(settings.FILE_STORAGE)()


def calc_max_width_height(org, max_width, max_height):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    if org_x / (max_width * 1.0) > org_y / (max_height * 1.0):
        return calc_max_width(org, max_width)
    else:
        return calc_max_height(org, max_height)


def calc_max_width(org, max_width):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    return max_width, int(org_y / (org_x / (1.0 * max_width)))


def calc_max_height(org, max_height):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    return int(org_x / (org_y / (1.0 * max_height))), max_height


def calc_min_width(org, min_width):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    return min_width, int(org_y / (org_x / (1.0 * min_width)))


def calc_min_height(org, min_height):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    return int(org_x / (org_y / (1.0 * min_height))), min_height


def calc_min_width_height(org, min_width, min_height):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    if org_x / (min_width * 1.0) > org_y / (min_height * 1.0):
        return calc_min_height(org, min_height)
    else:
        return calc_min_width(org, min_width)


def calc_size_min(org, min_size):
    org_x, org_y = (org[0] * 1.0, org[1] * 1.0)
    if org_x < org_y:
        return min_size, int(org_y / (org_x / (1.0 * min_size)))
    else:
        return int(org_x / (org_y / (1.0 * min_size))), min_size


def convert_raw_image(img, width=0, height=0, mode=1, enlarge=True, use_storage=None, quality=None):
    return _get_thumb(img, width=width, height=height, mode=mode, enlarge=enlarge,
                      bin_2_bin=True, use_storage=use_storage, quality=quality)


def convert_obj_image(img, width=0, height=0, mode=1, enlarge=True, use_storage=None, quality=None):
    return _get_thumb(img, width=width, height=height, mode=mode, enlarge=enlarge,
                      as_img=True, use_storage=use_storage, quality=quality)


def _get_thumb(img, width=0, height=0, mode=1, enlarge=True, bin_2_bin=False, as_img=False, use_storage=None, quality=None):
    '''
    modes:
    1 - fit to rectangle
    2 - crop
    3 - scale

    '''
    my_storage = use_storage or storage
    name = ''
    new_name = ''
    if as_img and img:
        pass
    elif isinstance(img, basestring) and not bin_2_bin:
        if not my_storage.exists(img):
            return ''  # TODO: fixme
        myfile = my_storage.open(img)
        name = img
    elif isinstance(img, File):
        myfile = img
        name = img.name
    elif isinstance(img, file):
        myfile = File(img)
        name = myfile.name
    elif hasattr(img, 'read') and hasattr(img, 'seek'):
        myfile = File(img)
        if not bin_2_bin:
            name = getattr(img, 'name', 'fakefile.jpg')
    if not name and not bin_2_bin and not as_img:
        return ''
    if name:
        bname, ext = os.path.splitext(name)
        new_name = 'thumbnails/' + bname.lstrip('/') + ("_%sx%s_%s%s" % (width, height, mode, ext))
        if not bin_2_bin and my_storage.exists(new_name):
            return my_storage.url(new_name)
    im = img if as_img else Image.open(myfile)
    w, h = im.size
    process_file = True
    if not enlarge and (width == 0 or width >= w) and (height == 0 or height >= h):
        process_file = False
        if bin_2_bin:
            myfile.seek(0)
            return myfile.read()
        elif as_img:
            return im
    im_format = im.format
    if height and not width:
        new_w, new_h = calc_max_height(im.size, height)
    elif width and not height:
        new_w, new_h = calc_max_width(im.size, width)
    elif width and height:
        if mode == 1:
            new_w, new_h = calc_max_width_height(im.size, width, height)
        else:
            new_w, new_h = width, height
    else:
        if bin_2_bin:
            myfile.seek(0)
            return myfile.read()
        elif as_img:
            return im
        return my_storage.url(name)

    if mode == 2:
        new_w1, new_h1 = calc_min_width_height(im.size, width, height)
        offset_w, offset_h = 0, 0
        if new_w1 > new_w:
            offset_w = (new_w1 - new_w) / 2
        else:
            offset_h = (new_h1 - new_h) / 2
        im = im.resize((new_w1, new_h1), Image.ANTIALIAS)
        im = im.crop((offset_w, offset_h, new_w + offset_w, new_h + offset_h))
    else:
        if process_file:
            im = im.resize((new_w, new_h), Image.ANTIALIAS)
    if as_img:
        return im
    fp = StringIO()
    # if new_name:
    #     fp.name = new_name
    save_kwargs = {}
    if quality:
        save_kwargs['quality'] = int(quality)
    im.save(fp, format=im_format, **save_kwargs)
    fp.seek(0)
    if bin_2_bin:
        return fp.read()
    if new_name:
        new_name = my_storage.save(new_name, fp)
        return my_storage.url(new_name)

make_thumbnail = _get_thumb
