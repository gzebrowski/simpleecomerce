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


def calc_by_proportion(w, h, proportion):
    if (w * 1.0) / h > proportion:
        val = int((1.0 * w) / proportion)
        return w, val, 0, (val - h) / 2
    else:
        val = int(1.0 * proportion * h)
        return val, h, (val - w) / 2, 0
